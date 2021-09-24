# nom

markdown note management helper

## installation

note: `nom` is written for python 3.

install with either:

    pip install nom

or from source:

    git clone https://github.com/frnsys/nom.git
    cd nom
    pip install --editable .

If you wish to use `nom clip` (to convert clipboard HTML into markdown notes) on OSX, you also need the following:

    pip install pyobjc

On Linux, you need `xclip` (version 0.13 or greater):

    apt install xclip

## usage

```
nom --help

Usage: nom [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  clip    convert html in the clipboard to markdown
  export  export a note to html
  preach  export a note to an html presentation
  view    view a note in the browse
```

A bit more about each command:

- `clip`: copy some text from a webpage, then run `nom clip -s ~/notes/foo.md`. This will save the html as markdown to `~/notes/foo.md` and also download any images to `~/notes/assets/foo/`.
    - if you don't pass `-s`, the markdown is output to stdout
    - pass `-e` to open the resulting markdown file in `EDITOR`. only available if `-s` is specified
    - pass `-v` to compile and then view the note in your browser
    - pass `-o` to overwrite an existing note, if there is one
- `view`: compiles and opens a note in the browser
    - pass `-w` to continually watch the original markdown file and its assets and recompile on changes
- `browse`: compiles notes in a directory and its subdirectories and opens in the browser
- `export`: to export a markdown file with its assets as a self-contained site, run `nom export ~/notes/foo.md .`. This will create a folder `foo` with the compiled note and its assets.
    - pass `-w` to continually watch the original markdown file and its assets and recompile on changes
    - pass `-v` to view the compiled note in your browser
    - pass `-s` with a path to a stylesheet to apply style overrides
- `preach`: similar to `export`, except it creates an HTML slideshow, interpreting `---` as slide breaks. Slides are advanced using the arrow keys. Accepts the same options as `export`.


## markdown extensions

`nom` supports the following extra markdown patterns:

- embed a pdf: `![](/path/to.pdf)`
- embed an mp4: `![](/path/to.mp4)`
    - to autoplay an mp4: `![](/path/to.mp4){: autoplay}`
- embed an mp3: `![](/path/to.mp3)`
- embed an iframe: `@[](https://web.site)`

A gallery element (target in stylesheet with `.gallery`):

```
+++
![Image A](assets/foo.jpg)
![Image B](assets/bar.jpg)
+++
```

## `preach`

For the `preach` there is some additional functionality.

First of all, when running a `preach` presentation it's recommended to use the Python HTTP server:

    python3 -m http.server 8001

You can visit `localhost:8001` in two separate browser tabs and the presentations will be synced. So you can run a copy on one screen and another on the projector.

### Included classes/attributes

There are also some built-in CSS classes for convenience:

- fullscreen iframe: `@[](https://web.site){: .fullscreen}`
- fullscreen background image: `![](/path/to.jpg){: .background}`

### Presenter mode

Presenter mode can be enabled with a `presenter` query param, e.g. `localhost:8001?presenter`. This mode does the following:

- Shows slide progress
- Shows a timer
- Shows speaker notes (see below)
- Synchronizes slides (see below)

#### Speaker notes

You can also include speaker notes as HTML comments, e.g.:

```

this is my slide

<!--
these are my notes for this slide.
-->

---

this is another slide

<!--
these are my notes for the second slide.
-->

```

#### Slide synchronization

Often you will want to have one browser tab with the presenter mode and another with the audience mode. When you advance the presenter mode, the audience mode tab should correspondingly advance too.

With `preach` there are two ways of synchronizing tabs:
    - _Local storage_ (default), for browser tabs open on the same device (i.e. computer connected to the projector via a direct connection, e.g. HDMI)
    - _p2p via WebRTC_, for browser tabs open on separate devices (i.e. laptop with presenter notes, and a separate computer connected to the projector). This requires an internet connection for both devices.

To use the p2p method, you must supply an additional `key` query parameter to both the presenter and audience mode tabs:
1. Open the presenter mode tab with a key of your choosing, e.g. `localhost:8001?presenter&key=foobar`. This tab will be designated the leader for the key `foobar`.
2. Open the audience mode tab with the same key, e.g. `localhost:8001?key=foobar`. This will follow the designated leader for the key `foobar`.

## Dev notes

The MathJax installed here is version 3.2.0. It's faster than 2.0 but lacking some features--most important newline (`\\`) support (see <https://github.com/mathjax/MathJax/issues/2312>). According to that issue it should be implemented some time next year.

To get the latest version of MathJax:

```
git clone https://github.com/mathjax/MathJax.git /tmp/mathjax
mv /tmp/mathjax nom/static/mathjax
```
