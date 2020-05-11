import os
import argparse
import json
import subprocess
import termcolor
import six


NO_COLORING = False


def colorize(text, color):
    if NO_COLORING or os.name == 'nt':
        return text
    else:
        return termcolor.colored(text, color)


def thisdir():
    path = os.path.abspath(os.path.realpath(__file__))
    path = path.split(os.path.sep)[:-1]
    return os.path.sep.join(path)


def workingdir():
    return os.getcwd()


def isDirRepo(path):
    return os.path.isdir(os.path.join(path, ".git"))


def execGitCommand(command,
                   repo,
                   silentOnSuccess=False,
                   noErrLogs=False):
    try:
        if noErrLogs:
            subprocess.check_output(["git"] + command,
                                    stderr=subprocess.PIPE,
                                    cwd=repo["repo"])
        else:
            subprocess.check_output(["git"] + command,
                                    cwd=repo["repo"])
    except Exception:
        print("%s %s" % (repo["formattedName"],
                         colorize("[failed]",
                                  "red")))
        return False
    else:
        if not silentOnSuccess:
            print("%s %s" % (repo["formattedName"],
                             colorize("[ok]",
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
        if six.PY3:
            branch = branch.decode("ascii")
    except Exception:
        branch = colorize("<unknown>", "red")
    return branch


def isRepoClean(repo):
    return not len(subprocess.check_output(["git",
                                            "status",
                                            "--porcelain"],
                                           cwd=repo))


def hasRepoUnpushedCommits(repo):
    try:
        status = subprocess.check_output(["git",
                                          "status"],
                                         stderr=subprocess.PIPE,
                                         cwd=repo)
        if six.PY3:
            status = status.decode("ascii")
        return "use \"git push\" to publish your local commits" in status
    except Exception:
        return False


def isInUpstream(repo):
    try:
        subprocess.check_output(["git",
                                 "rev-parse",
                                 "--abbrev-ref",
                                 "--symbolic-full-name",
                                 "@{u}"],
                                stderr=subprocess.PIPE,
                                cwd=repo)
    except Exception:
        return False
    else:
        return True


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
        inUpstream = isInUpstream(repo)
        repos.append({
            "repo": repo,
            "name": repoName,
            "branch": branch,
            "clean": clean,
            "unpushed": unpushed,
            "inUpstream": inUpstream,
            "valid": branch != colorize("<unknown>", "red")
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
            clean = colorize("clean", "green")
        else:
            clean = colorize("dirty", "red")
        clean = clean.ljust(17)
        if repo["unpushed"]:
            unpushed = colorize("unpushed", "red")
        elif not repo["valid"]:
            unpushed = colorize("????????", "red")
        else:
            unpushed = colorize("pushed", "green")
        unpushed = unpushed.ljust(18)
        if repo["inUpstream"]:
            inUpstream = colorize("remote", "green")
        else:
            inUpstream = colorize("local", "red")
        if not silent:
            print("%s %s %s %s %s" % (repoName,
                                      branch,
                                      clean,
                                      unpushed,
                                      inUpstream))
    return repos


def handlePullOp(root):
    repos = handleStatusOp(root, True)
    for repo in repos:
        if repo["valid"]:
            execGitCommand(["pull"], repo)
        else:
            print("%s %s" % (repo["formattedName"],
                             colorize("[skipped]",
                                      "yellow")))


def handlePushOp(root):
    repos = handleStatusOp(root, True)
    for repo in repos:
        if (repo["unpushed"] or not repo["inUpstream"]) and repo["valid"]:
            command = ["push"]
            if not repo["inUpstream"]:
                command = ["push", "-u", "origin", repo["branch"]]
            execGitCommand(command, repo, False, True)
        else:
            print("%s %s" % (repo["formattedName"],
                             colorize("[skipped]",
                                      "yellow")))


def handleCommitOp(root, msg):
    repos = handleStatusOp(root, True)
    if msg is None:
        msg = six.moves.input("Enter commit message: ")
    for repo in repos:
        if not repo["clean"] and repo["valid"]:
            if execGitCommand(["add", "."], repo, True):
                execGitCommand(["commit", "-m", msg], repo)
        else:
            print("%s %s" % (repo["formattedName"],
                             colorize("[skipped]",
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
                             colorize("[skipped]",
                                      "yellow")))
    print(colorize("\nIn case of switching to nonexistent " +
                   "branch, you must provide parameter --new!",
                   "red"))


def main():
    global NO_COLORING
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", help="Action to be performed")
    parser.add_argument("-m", "--message",
                        required=False,
                        help="Commit message")
    parser.add_argument("-n", "--new",
                        action="store_true",
                        required=False,
                        help="When specified, new branch is " +
                        "created during checkout")
    parser.add_argument("-b", "--branch",
                        required=False,
                        help="Name of branch to be switched to")
    parser.add_argument("--no-color",
                        action="store_true",
                        required=False,
                        help="Disables coloring")
    args = parser.parse_args()
    NO_COLORING = args.no_color
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
