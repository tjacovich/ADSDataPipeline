
This directory holds some rough code used to validate data from the
old and new pipeline.

The code is rough in that is is not fully automated.  There are script
files that run on postgres instances to export data to files from the
master pipeline database.  There are python files that compare two
export data files.

On reflection, this python code should have used assert and perhaps
shared code with the existing unit test code.  Once we switch to the
new pipeline this code will not be useful.
