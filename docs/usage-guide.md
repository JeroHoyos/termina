# Usage guide

## The window

| Area | Contents |
| --- | --- |
| Top | The list of talks, the resolution of the talk, *Render pending*, *Present* and *Export*. |
| Left | The slides, in the order of the talk, each with its status. |
| Center | The video of the selected slide, its resolution and its review. |
| Right | The Claude chat. For more information, refer to [Claude chat](claude-chat.md). |
| Bottom | The job that runs, with its progress and *Cancel*. *Log* shows the output of each job. |

![The window, with a talk of three slides](images/window.png)

Drag the line between the center and the chat to change the width of the chat. Push Ctrl and + or
Ctrl and - to change the size of the contents.

## Keys

| Key | Result |
| --- | --- |
| Up arrow, Down arrow | Selects the slide before or the slide after. |
| Page Up, Page Down | Moves ten slides in the list. |
| Home, End | Selects the first slide or the last slide. |
| Left arrow, Right arrow | Goes to the pause before or to the pause after. |
| Space | Plays the video or stops it. |
| F2 | Changes the name of the slide. |
| Ctrl+F | Opens *Find in the slides*. |
| Esc | Closes a menu or the log. In the chat, Esc stops Claude. |

The keys work when the cursor is not in a text box and not in the chat.

## Make the slides with Claude

1. Select the talk in the list at the top.
2. The first time, click *Render pending*.
3. Type a request in the chat. For example: `/slides git: a new slide after git_diff that explains git stash`.
4. Wait for Claude. The app shows each step while Claude works.
5. Examine the video of the slide in the center.
6. Write what to change in *Review*, then click *Send to Claude*.
7. When the slide is correct, click *Approve*.

To send many changes together, write each note and click *Save note*. Then click
*Send N changes to Claude* at the top.

To show Claude an image with the note, click *Attach image*. You can also paste or drop the image
in *Review*. The images go to Claude with the note. The app keeps the images that you did not send
only until you close it.

## Mark on the slide

To show what you want to change, mark it on the slide. The marks go to Claude as an image.

1. Stop the video at the moment that you want to mark.
2. Click *Mark on the slide* in *Review*.
3. Select a tool and mark the frame.
4. Click *Add to the note*.

| Tool | Procedure | Result |
| --- | --- | --- |
| *Point* | Click a part of the slide. Then write what to change there. | A point with a number. The text goes into the note with that number. |
| *Draw* | Drag on the slide. | A line, for example around an element. |
| *Move* | Drag from an element to its new position. | An arrow. |

*Undo* or Ctrl+Z removes the last mark. *Cancel* or Esc closes the marks and adds nothing.

![Marks on a slide: a point, a circle and an arrow](images/mark.png)

The app keeps the text of a note that you did not save or send, until you close the app.

![A slide with a saved note and the button Send 1 change to Claude at the top](images/review.png)

The first render of a talk installs its Python packages. This takes some minutes.

## The status of a slide

| Status | Definition |
| --- | --- |
| up to date | The video agrees with the code. |
| not rendered | The slide has no video. |
| changed | The `.py` file of the slide changed after the render. |
| previous slide changed | The slide before it changed. The transition into this slide is old. |
| shared code changed | A file that many slides use changed, for example the style. Render again only if the slide uses it. |
| page number changed | The slide has a different page number from its video. |
| different resolution | The video has a different resolution from the slide. A slide without its own resolution uses the resolution of the talk. |
| commented out | The call of the slide in `main.py` is a comment. The talk does not show it. |

If a file holds many slides, a change to that file changes the status of all of them.

An approval is valid only for the code that you approved. If the code of the slide changes, the
review goes back to *to review*.

## Change the slides of a talk

All these actions are in the *⋯* menu of the slide and in the context menu of the list.

![The menu of a slide: Rename, Move up, Move down, New slide after this one and Delete](images/slide-menu.png)

| Action | Procedure | Result |
| --- | --- | --- |
| Add a slide | Click *+ New*. Type a name and select the slide that comes before it. | The app makes the file from the template of the talk, registers it and puts it in `main.py`. If you write what the slide shows, the app sends the request to Claude. |
| Move a slide | Drag the slide in the list, with the *All* filter. Or use *Move up* and *Move down*. | The slides that get a new transition change to *previous slide changed*. |
| Rename a slide | Double-click the title, or push F2, or select *Rename*. | The app also renames the videos. It is not necessary to render the slide again. |
| Make a group of slides | Select *Start a group here* in the menu of the first slide of the group. Type a name and push Enter. | The group goes from that slide to the start of the next group. The app writes the name as a comment in `main.py`. |
| Hide or show a group | Click the name of the group. | The list hides the slides of the group. The talk does not change. |
| Add a slide or a group with the right button | Right-click a slide, the name of a group or the empty part of the list. | The menu makes a slide or starts a group at that place. In the empty part, the menu uses the selected slide. |
| Rename or remove a group | Right-click the name of the group. | When you remove a group, its slides stay in the talk and go to the group before. |
| Delete a slide | Select *Delete…*. | The file of the slide goes to the recycle bin of Windows. You can get it back from there. |
| Hide a slide | Select *Hide from the talk*. | The call in `main.py` becomes a comment. The talk does not show the slide. Its file and its videos stay. |
| Put back a slide | Select a slide with the status *commented out*, then click *Put it back*. | The call in `main.py` is not a comment now. |

## Colors and page numbers

Click the **ⓘ** button next to the list of talks.

- *Colors of the slides* changes the background, the text and the accent color of all the slides.
  Only the talks that the app made have this option.
- *Number the slides* puts a page number in the corner of each slide.

Render the slides again after a change. The moon button at the top changes the window between
light and dark. It does not change the slides.

## Resolution

- The resolution at the top (480p, 720p or 1080p) is the resolution of the talk. The app keeps it
  in the `talk.manimrs` file of the talk.
- A slide can have its own resolution. Select it next to the status of the slide.
- A slide without its own resolution uses the resolution of the talk. If its video has a different
  resolution, the slide is *different resolution* until you render it again.
- When you change the resolution of the talk, *Render pending* renders again the slides that use it.

A slide takes approximately 10 seconds at 480p and 30 seconds at 1080p. Use 480p to examine the
slides and 1080p to present them.

## Edit on the slide

Click *Edit on the slide* below the video. The app shows a box on each object of the pause.

| Action | Procedure | Result |
| --- | --- | --- |
| Move an object | Drag its box. | The app adds one line to the code of the slide and renders the slide again. |
| Change a text | Double-click a text or a formula, then type the new text. | The app changes that text in the code. |
| Add an element | Select it in *Add an element…*, then click the slide. | The element goes in at the end of the pause that you see: a text, a formula, a rectangle, a circle, an arrow, a picture, a sphere, a cube or 3D axes. |

The app can move an object only if the code gives it a name of its own. If the object is in a
group, the group moves. If the code makes the object in a loop, mark it and ask Claude to move it.
Render the slide before you edit it again.

## Find and replace

1. Click the search button above the list of slides, or push Ctrl+F.
2. Type the text and click *Find*. The app looks in the text of the slides and in the speaker notes.
3. Click a result to go to its slide.
4. To change the text in all the talk, type the new text in *Replace with* and click *Replace all*.

The app changes only the text between quotation marks in the code. Thus a replacement cannot change
the name of a variable. The slides that change must be rendered again.

## Speaker notes

Write what you want to say in *Speaker notes*, below *Review*. The app saves the notes when you
click out of the box. A change to the notes does not render the slide again.

*Only on this pause* holds the notes of the pause that the video shows. The presenter shows them
after the notes of the slide.

The presenter shows the notes in its second window, if the computer has two screens. The HTML and
PowerPoint exports also have the notes. The app keeps the notes in the `speaker-notes.json` file of
the talk.

## Present a talk

1. Click *Present*.
2. Push the right arrow key to go to the next pause.
3. Push the left arrow key to go back.

| Key | Result |
| --- | --- |
| F | Change between full screen and a window. |
| Esc | Leave full screen. |
| Q | Close the presenter. |

The presenter shows only the slides that have a video. It tells you the names of the slides that it
does not show.

## Export a talk

| Export | Result | Use |
| --- | --- | --- |
| HTML folder (.zip) | `diapos/exported/<talk>.zip` in the folder of the talk. | Unzip it on the other device and open `<talk>.html` with Chrome, Edge, Firefox or Safari. A connection to the internet is not necessary. |
| PDF (.pdf) | `diapos/exported/<talk>.pdf` | Each pause is a page. The page shows the last frame of the pause. A loop gets no page if a pause comes before it in its slide, because the loop ends on that page. The PDF export needs FFmpeg. |
| Narrated video (.mp4) | `diapos/exported/<talk>-narrated.mp4` | A voice of the system says the speaker notes of each pause, then the video goes to the next pause. On Linux, the voice needs espeak-ng. |
| Video (.mp4) | `diapos/exported/<talk>.mp4` | All the slides in one video, at the resolution of the talk. The video has no pauses. |
| PowerPoint (.pptx) | `diapos/exported/<talk>.pptx` | Each pause is a page with its video. The speaker notes go into the notes of each page. |
| Talk package (.zip) | `diapos/exported/<talk>-talk.zip` | The code and the videos of the talk. Unzip it on the other device and open its folder with Termina. All the slides are up to date. |
| One slide (.mp4, .gif) | `diapos/exported/<slide>.mp4` or `.gif` | Open the menu of the slide and select *Export as video* or *Export as GIF*. |

![The Export menu](images/export.png)

The export has only the slides that have a video. Render all the slides at 1080p before you export.

The first HTML export downloads reveal.js. For that export, a connection to the internet is necessary.
