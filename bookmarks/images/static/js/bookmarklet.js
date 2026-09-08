(function(){
  var jquery_version = '3.7.1';
  var site_url = '//127.0.0.1:8000/';
  var static_url = site_url + 'static/';
  var min_width = 100;
  var min_height = 100;

  function bookmarklet(msg) {
    // Load CSS
    var css = jQuery('<link>');
    css.attr({
      rel: 'stylesheet',
      type: 'text/css',
      href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random() * 99999999999999999999)
    });
    jQuery('head').append(css);

    // Remove existing bookmarklet if any
    jQuery('#bookmarklet').remove();

    // Load HTML modal
    var box_html = '<div id="bookmarklet">' +
      '<div class="bookmarklet-header">' +
        '<span>Select an image to bookmark:</span>' +
        '<a href="#" id="close">&times;</a>' +
      '</div>' +
      '<div class="images"></div>' +
    '</div>';
    jQuery('body').append(box_html);

    // Close event
    jQuery('#bookmarklet #close').click(function(e){
      e.preventDefault();
      jQuery('#bookmarklet').remove();
    });

    // Find images on the page and display them
    var count = 0;
    jQuery.each(jQuery('img'), function(index, image) {
      var src = jQuery(image).attr('src');
      if (src) {
        // Resolve relative URLs to absolute URLs
        var img = new Image();
        img.src = src;
        var fullSrc = img.src;

        if ((jQuery(image).width() >= min_width && jQuery(image).height() >= min_height) ||
            (image.naturalWidth >= min_width && image.naturalHeight >= min_height)) {
          count++;
          jQuery('#bookmarklet .images').append(
            '<a href="#" class="bookmarklet-item"><img src="' + fullSrc + '" /></a>'
          );
        }
      }
    });

    if (count === 0) {
      jQuery('#bookmarklet .images').append('<p class="no-images">No large images found on this page.</p>');
    }

    // When an image is selected, open URL to bookmark it
    jQuery('#bookmarklet .images a').click(function(e){
      e.preventDefault();
      var selected_image = jQuery(this).children('img').attr('src');
      jQuery('#bookmarklet').hide();
      window.open(
        site_url + 'images/create/?url=' +
        encodeURIComponent(selected_image) +
        '&title=' +
        encodeURIComponent(document.title || 'Bookmarked Image'),
        '_blank'
      );
    });
  }

  // Check if jQuery is loaded
  if (typeof window.jQuery != 'undefined') {
    bookmarklet();
  } else {
    var script = document.createElement('script');
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/' + jquery_version + '/jquery.min.js';
    document.head.appendChild(script);

    var attempts = 20;
    (function checkJQuery(){
      if (typeof window.jQuery == 'undefined') {
        if (--attempts > 0) {
          window.setTimeout(checkJQuery, 200);
        } else {
          alert('An error occurred while loading jQuery for the bookmarklet.');
        }
      } else {
        bookmarklet();
      }
    })();
  }
})();
