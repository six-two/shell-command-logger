# Output files

## Directory structure

Command outputs for each program is stored in a separate folder.
For example all invocations of `nmap` will be stored in a folder called `nmap`.

Each output is stored in three files:

- `<time>.log` contains the raw output.
  You can `cat` this file to see the whole output with colors and everything.
  However, some output may look broken if your terminal has a different size than the terminal this command was recorded in.
- `<time>.time` contains timing info for `scriptreplay`.
  This file can be used in combination with `<time>.log` to replay the command output in real time.
- `<time>.json` contains metadata such as:
    - the start and end time of the process
    - the full command line used to start the process
    - the exit code if the process
    - the username and hostname combination, that was used to run the command


### Example

After recording a single command, your data directory will likely look like this:

```bash
$ scl log echo a
[INFO] Created README file in output directory
a
$ tree ~/.shell-command-logs/
/home/<user>/.shell-command-logs/
├── echo
│   ├── 2022w22g_123504_1144.json
│   ├── 2022w22g_123504_1144.log
│   └── 2022w22g_123504_1144.time
└── README.md
```

## README file

If `create-readme` is set to `True` (default setting), then a README file is created in the root of the data directory.
It contains some basic information about the structure of the folder and basic instructions on how to replay the files.
This is useful, if you give the data to someone else, who has never heard of this program.

## Date format
The normal (Gregorian) caledar is not very intuitive.
Thus I have decided to use an alternative date format, that uses the week number and the type of day.
The format is `<YYYY>w<WW><D>` where

- `<YYYY>` is the current year (like `2022`)
- `w` is an indicator, that teh follwoing is a week and not a month
- `<WW>` is the number of the current week. 
- `<D>` is the day type expressed as a letter (`a` -> Monday, `b` -> Tueday, ..., `g` -> Sunday)

For example the Tuesday of the 9th week in 2022 would be written as `2022w09b`.

This format is similar to [ISO 8601 week dates](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) (which formats dates like `2022-W092`), but with the following differences:

- The separator between the year and month is `w` instead of `-W` to make the dates shorter (and easier to type)
- Instead of using a number for the day of the week a letter is used.
This should be less confusing and still makes dates sortable by lexicographical order

You can obtain today's date in this format with the following bash command:
```bash
echo $(date +%Gw%V)$(date +%u | tr '[1-7]' '[a-g]')
```
