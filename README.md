# Shell command logger

## Date format
The normal (Gregorian) caledar is not very intuitive.
Thus I have decided to allow an alternative date format, that uses the week number and the type of day.
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
