---
title: Morris.js
---

### 1. Screenshot

<div class="screenshot-holder">

[![screenshot](assets/images/demo/appkit-chart-flot.jpg){: .img-responsive}](https://wrapbootstrap.com/theme/admin-appkit-admin-theme-angularjs-WB051SCJ1?ref=3wm)
[*&nbsp;*{: .icon .fa .fa-link}](https://wrapbootstrap.com/theme/admin-appkit-admin-theme-angularjs-WB051SCJ1?ref=3wm){: .mask}

</div>


### 2. Getting Started

Add **morris.js** and its dependencies ([jQuery](#) & [Raphaël](#)) to your page.

```html
1 <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/morris.js/0.5.1/morris.css">
2 <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>
3 <script src="//cdnjs.cloudflare.com/ajax/libs/raphael/2.1.0/raphael-min.js"></script>
4 <script src="//cdnjs.cloudflare.com/ajax/libs/morris.js/0.5.1/morris.min.js"></script>
```


### 3. Your first chart

Start by adding a `<div>` to your page that will contain your chart. Make sure it has an ID so you can refer to it in your Javascript later.

```html
<div id="myfirstchart" style="height: 250px;"></div>
```

<div class="callout-block callout-info"><div class="icon-holder">*&nbsp;*{: .fa .fa-info-circle}
</div><div class="content">
{: .callout-title}
#### Note:

in order to display something, you’ll need to have given the div some dimensions.
Here I’ve used inline CSS just for illustration.

</div></div>

Next add a `<script>` block to the end of your page, containing the following javascript code:

```javascript
new Morris.Line({
  // ID of the element in which to draw the chart.
  element: 'myfirstchart',
  // Chart data records -- each entry in this array corresponds to a point on
  // the chart.
  data: [
    { year: '2008', value: 20 },
    { year: '2009', value: 10 },
    { year: '2010', value: 5 },
    { year: '2011', value: 5 },
    { year: '2012', value: 20 }
  ],
  // The name of the data record attribute that contains x-values.
  xkey: 'year',
  // A list of names of data record attributes that contain y-values.
  ykeys: ['value'],
  // Labels for the ykeys -- will be displayed when you hover over the
  // chart.
  labels: ['Value']
});
```
