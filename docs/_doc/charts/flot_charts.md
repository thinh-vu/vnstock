---
title: Flot Charts
---

### 1. Screenshot

<div class="screenshot-holder">

[![screenshot](assets/images/demo/appkit-chart-flot.jpg){: .img-responsive}](https://wrapbootstrap.com/theme/admin-appkit-admin-theme-angularjs-WB051SCJ1?ref=3wm)
[*&nbsp;*{: .icon .fa .fa-link}](https://wrapbootstrap.com/theme/admin-appkit-admin-theme-angularjs-WB051SCJ1?ref=3wm){: .mask}

</div>


### 2. Basic Usage

*&nbsp;*{: .fa .fa-external-link-square} **Source:** <https://github.com/flot/flot/blob/master/README.md>

Create a placeholder div to put the graph in:

```html
<div id="placeholder"></div>
```

You need to set the width and height of this div, otherwise the plot library doesn't know how to scale the graph. You can do it inline like this:

```html
<div id="placeholder" style="width:600px;height:300px"></div>
```

You can also do it with an external stylesheet. Make sure that the placeholder isn't within something with a display:none CSS property - in that case, Flot has trouble measuring label dimensions which results in garbled looks and might have trouble measuring the placeholder dimensions which is fatal (it'll throw an exception).

Then when the div is ready in the DOM, which is usually on document ready, run the plot function:

```javascript
$.plot($("#placeholder"), data, options);
```

Here, data is an array of data series and options is an object with settings if you want to customize the plot. Take a look at the examples for some ideas of what to put in or look at the [API reference](#). Here's a quick example that'll draw a line from (0, 0) to (1, 1):

```javascript
$.plot($("#placeholder"), [ [[0, 0], [1, 1]] ], { yaxis: { max: 1 } });
```

The plot function immediately draws the chart and then returns a plot object with a couple of methods.
