
=============================
Test are regularly broken #12
=============================

ISSUE URL: https://github.com/sveetch/dependency-comb/issues/12

This is a study about this bug which exists since long ago.

In this directory there are some *.log files that have been runned under different
system dates.

This was to see if 'humanize' was doing some rounding depending current date. At least
these with these two logs, nothing can let thinking about a rounding bug.

At the time of writing this document, we will so update again the tests to fit to new
humanized dates returned from processors (meaning the logs will have different
humanized content). We hope these logs could help to find the reason of thi bug next
time it happen.

At this point we are sure about:

* 'freeze_time' in tests is not bypassed, formatter always use the expected frozen date
  in tests;
* Upgrading humanizer to the very last release did not fix anything;
* Using two different dates does not raise anything to find cause of the issue;

What we thought:

* Maybe 'humanizer.naturaldata' is rounding some value that lead to variadic
  humanizations (24days become 1month) but i did not find any info about this;
* Analyzer use well the given test data and does not make any request outside that
  would change computation against data;
