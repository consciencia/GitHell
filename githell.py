import os
import argparse
import json
import subprocess
import termcolor
import six


def thisdir():
    path = os.path.abspath(os.path.realpath(__file__))
    path = path.split(os.path.sep)[:-1]
    return os.path.sep.join(path)


def workingdir():
    return os.getcwd()


def isDirRepo(path):
    return os.path.isdir(path + os.path.sep + ".git")


def execGitCommand(command, repo):
    try:
        subprocess.check_output(["git"] + command,
                                cwd=repo["repo"])
    except Exception:
        print("%s %s" % (repo["formattedName"],
                         termcolor.colored("[failed]",
                                           "red")))
        return False
    else:
        print("%s %s" % (repo["formattedName"],
                         termcolor.colored("[ok]",
                                           "green")))
        return True


def getRepoBranch(repo):
    try:
        branch = subprocess.check_output(["git",
                                          "rev-parse",
                                          "--abbrev-ref",
                                          "HEAD"],
                                         stderr=subprocess.PIPE,
                                         cwd=repo)[:-1]
    except Exception:
        branch = termcolor.colored("<unknown>", "red")
    return branch


def isRepoClean(repo):
    return not len(subprocess.check_output(["git",
                                            "status",
                                            "--porcelain"],
                                           cwd=repo))


def hasRepoUnpushedCommits(repo):
    try:
        return not not len(subprocess.check_output(["git",
                                                    "log",
                                                    "--branches",
                                                    "@{u}.."],
                                                   stderr=subprocess.PIPE,
                                                   cwd=repo))
    except Exception:
        return False


def handleStatusOp(root, silent=False):
    allDirs = os.listdir(root)
    allDirs = [root + os.path.sep + d for d in allDirs]
    allDirs = [d for d in allDirs if os.path.isdir(d) and isDirRepo(d)]
    repos = []
    maxNameLen = 0
    maxBranchLen = 0
    for repo in allDirs:
        repoName = repo.split(os.path.sep)[-1]
        branch = getRepoBranch(repo)
        clean = isRepoClean(repo)
        unpushed = hasRepoUnpushedCommits(repo)
        repos.append({
            "repo": repo,
            "name": repoName,
            "branch": branch,
            "clean": clean,
            "unpushed": unpushed,
            "valid": branch != termcolor.colored("<unknown>", "red")
        })
        if len(repoName) > maxNameLen:
            maxNameLen = len(repoName)
        if len(branch) > maxBranchLen:
            maxBranchLen = len(branch)
    for repo in repos:
        repoName = repo["name"].ljust(maxNameLen + 2)
        repo["formattedName"] = repoName
        if ord(repo["branch"][0]) == 27:
            branch = repo["branch"].ljust(maxBranchLen + 9)
        else:
            branch = repo["branch"].ljust(maxBranchLen)
        repo["formattedBranch"] = branch
        if repo["clean"]:
            clean = termcolor.colored("clean", "green")
        else:
            clean = termcolor.colored("dirty", "red")
        clean = clean.ljust(15)
        if repo["unpushed"]:
            unpushed = termcolor.colored("unpushed", "red")
        else:
            unpushed = termcolor.colored("pushed", "green")
        if not silent:
            print("%s %s %s %s" % (repoName,
                                   branch,
                                   clean,
                                   unpushed))
    return repos


def handlePullOp(root):
    repos = handleStatusOp(root, True)
    for repo in repos:
        if repo["valid"]:
            execGitCommand(["pull"], repo)
        else:
            print("%s %s" % (repo["formattedName"],
                             termcolor.colored("[skipped]",
                                               "yellow")))


def handlePushOp(root):
    repos = handleStatusOp(root, True)
    for repo in repos:
        if repo["unpushed"] and repo["valid"]:
            execGitCommand(["push"], repo)
        else:
            print("%s %s" % (repo["formattedName"],
                             termcolor.colored("[skipped]",
                                               "yellow")))


def handleCommitOp(root, msg):
    repos = handleStatusOp(root, True)
    if msg is None:
        msg = six.moves.input("Enter commit message: ")
    for repo in repos:
        if not repo["clean"] and repo["valid"]:
            if execGitCommand(["add", "."], repo):
                execGitCommand(["commit", "-m", msg], repo)
        else:
            print("%s %s" % (repo["formattedName"],
                             termcolor.colored("[skipped]",
                                               "yellow")))


def handleCheckoutOp(root, branch, new):
    repos = handleStatusOp(root, True)
    for repo in repos:
        if not repo["clean"] and repo["valid"]:
            command = ["checkout", branch]
            if new:
                command = ["checkout", "-b", branch]
            execGitCommand(command, repo)
        else:
            print("%s %s" % (repo["formattedName"],
                             termcolor.colored("[skipped]",
                                               "yellow")))
    print(termcolor.colored("\nIn case of switching to nonexistent " +
                            "branch, you must provide parameter --new!",
                            "red"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", help="Action to be performed")
    parser.add_argument("-m", "--message",
                        required=False,
                        help="Commit message")
    parser.add_argument("-n", "--new",
                        required=False,
                        action="store_true",
                        help="When specified, new branch is " +
                        "created during checkout")
    parser.add_argument("-b", "--branch",
                        required=False,
                        help="Name of branch to be switched to")
    args = parser.parse_args()
    operation = args.operation
    if operation == "debug":
        state = handleStatusOp(workingdir(), True)
        print(json.dumps(state, indent=4))
    elif operation == "status":
        handleStatusOp(workingdir())
    elif operation == "pull":
        handlePullOp(workingdir())
    elif operation == "push":
        handlePushOp(workingdir())
    elif operation == "commit":
        handleCommitOp(workingdir(), args.message)
    elif operation == "checkout":
        if not args.branch:
            print("Missing --branch option!")
            exit(1)
        handleCheckoutOp(workingdir(), args.branch, args.new)
    else:
        print("Unknown operation '%s'!" % operation)
        exit(1)


if __name__ == "__main__":
    main()
