import os
import argparse
import json
import subprocess
import termcolor


def thisdir():
    path = os.path.abspath(os.path.realpath(__file__))
    path = path.split(os.path.sep)[:-1]
    return os.path.sep.join(path)


def workingdir():
    return os.getcwd()


def isDirRepo(path):
    return os.path.isdir(path + os.path.sep + ".git")


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


def handleListOp(root, silent=False):
    allDirs = os.listdir(root)
    allDirs = [root + os.path.sep + d for d in allDirs]
    allDirs = [d for d in allDirs if os.path.isdir(d) and isDirRepo(d)]
    repos = []
    for repo in allDirs:
        repoName = repo.split(os.path.sep)[-1]
        branch = getRepoBranch(repo)
        clean = isRepoClean(repo)
        repos.append({
            "repo": repo,
            "name": repoName,
            "branch": branch,
            "clean": clean,
            "valid": branch != termcolor.colored("<unknown>", "red")
        })
        if not silent:
            repoName = repoName.ljust(25)
            if ord(branch[0]) == 27:
                branch = branch.ljust(44)
            else:
                branch = branch.ljust(35)
            if clean:
                clean = termcolor.colored("clean", "green")
            else:
                clean = termcolor.colored("dirty", "red")
            print("%s %s %s" % (repoName, branch, clean))
    return repos


def handlePullOp(root):
    repos = handleListOp(root, True)
    for repo in repos:
        repoName = repo["name"].ljust(25)
        if repo["valid"]:
            try:
                subprocess.check_output(["git",
                                         "pull"],
                                        cwd=repo["repo"])
            except Exception:
                print("%s [failed]" % repoName)
            else:
                print("%s [ok]" % repoName)
        else:
            print("%s [skipped]" % repoName)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", help="Action to be performed")
    args = parser.parse_args()
    operation = args.operation
    if operation == "list":
        handleListOp(workingdir())
    elif operation == "pull":
        handlePullOp(workingdir())
    else:
        print("Unknown operation '%s'!" % operation)
        exit(1)


if __name__ == "__main__":
    main()
