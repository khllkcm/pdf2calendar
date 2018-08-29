# pdf2calendar

Automatically parse a PDF timetable and add it to Google Calendar using Python OpenCV and Tesseract.

![alt text](screenshot.jpg)

This is specific to my use case but the code can be easily repurposed to support other content layouts.

# Usage

```python pdf2calendar.py [-h] -f FILE -g GROUP -s START -e END [-t TIMEZONE]```

### Example:

```python pdf2calendar.py -f ~/Documents/emploi.pdf -g B -s 28/8/2018 -e 30/4/2019```


# Setup

1. Clone this repository `git clone https://github.com/khllkcm/pdf2calendar.git`

2. Install the required system packages listed at the `dependencies` folder

3. Place `dependencies/essai.traineddata` in your system's `tessdata` directory.

4. Install the required Python packages `pip install --user -r requirements.txt`
