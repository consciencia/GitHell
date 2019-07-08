# GitHell
Tool for managing multiple git repositories at once.

Anyway, If you wonder why this tool is named githell, its because
managing multiple repositories which are part of one project
is literally **hell** on earth.

## Installation
```
$ pip install termcolor
$ git clone https://github.com/consciencia/GitHell.git
$ cd GitHell
$ sudo ./install.sh
```

## Usage
First, navigate to directory where all your repositories reside.

For printing status of your repositories, type:
```
$ githell status
```

For pulling of all valid repositories, type:
```
$ githell pull
```

For pushing all unpushed commits, type:
```
$ githell push
```

For commiting changes from all dirty repositories, type:
```
$ githell commit
```

For switching to existing branch in all dirty repositories, type:
```
$ githell --branch ${branchName} checkout
```

For switching to non-existent branch in all dirty repositories, type:
```
$ githell --branch ${branchName} --new checkout
```

## TODO
1) Add support for work groups.
2) Bulk diff.
