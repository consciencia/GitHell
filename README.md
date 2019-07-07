# GitHell
Tool for managing multiple git repositories at once.

Anyway, If you wonder why this tool is named githell, its because managing multiple repositories which are part of one project is **hell**. 

## Installation
```
$ pip install termcolor
$ git clone https://github.com/consciencia/GitHell.git
$ cd GitHell
$ sudo ./install.sh
```

## Usage
First, navigate to directory where all your repositories reside.

For listing your repositories together with limited status information, type:
```
$ githell list
```

For pulling of all valid repositories, type:
```
$ githell pull
```

## TODO
1) Extend **list** operation so that it will output if some unpushed commits are present in repo.
2) Add support for bulk branch creation.
3) Add support for bulk commit.
4) Add support for bulk push.
5) Add support for bulk branch swithing.
