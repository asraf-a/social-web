(function(){
  var old = document.getElementById('bookmarklet');
  if (old) { old.remove(); }

  var cssText = '#bookmarklet{position:fixed;top:20px;right:20px;width:420px;max-height:85vh;background:rgba(15,23,42,0.96);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.18);border-radius:16px;box-shadow:0 20px 25px -5px rgba(0,0,0,0.5),0 8px 10px -6px rgba(0,0,0,0.5);z-index:2147483647;padding:1.25rem;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;color:#f8fafc;display:flex;flex-direction:column;box-sizing:border-box;}' +
    '#bookmarklet *{box-sizing:border-box;}' +
    '#bookmarklet .bm-head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.12);padding-bottom:0.75rem;margin-bottom:1rem;font-size:1rem;font-weight:700;color:#fff;}' +
    '#bookmarklet .bm-close{color:#94a3b8;font-size:1.6rem;text-decoration:none;line-height:1;cursor:pointer;}' +
    '#bookmarklet .bm-close:hover{color:#fff;}' +
    '#bookmarklet .bm-images{display:grid;grid-template-columns:repeat(2,1fr);gap:0.75rem;overflow-y:auto;max-height:calc(85vh - 80px);padding-right:4px;}' +
    '#bookmarklet .bm-item{display:block;height:130px;border-radius:8px;overflow:hidden;border:2px solid transparent;background:#1e293b;cursor:pointer;text-decoration:none;transition:all 0.2s ease;}' +
    '#bookmarklet .bm-item:hover{border-color:#6366f1;transform:scale(1.03);}' +
    '#bookmarklet .bm-item img{width:100%;height:100%;object-fit:cover;display:block;}' +
    '#bookmarklet .bm-empty{padding:1.5rem;text-align:center;color:#94a3b8;font-size:0.9rem;grid-column:span 2;}';

  var style = document.getElementById('bm-styles');
  if (!style) {
    style = document.createElement('style');
    style.id = 'bm-styles';
    style.textContent = cssText;
    document.head.appendChild(style);
  }

  var container = document.createElement('div');
  container.id = 'bookmarklet';

  var head = document.createElement('div');
  head.className = 'bm-head';
  head.innerHTML = '<span>Select an image to bookmark:</span><span class=\'bm-close\'>&times;</span>';
  container.appendChild(head);

  var imgList = document.createElement('div');
  imgList.className = 'bm-images';
  container.appendChild(imgList);

  document.body.appendChild(container);

  head.querySelector('.bm-close').onclick = function(){ container.remove(); };

  var imgs = document.querySelectorAll('img');
  var count = 0;
  var seen = {};

  for (var i = 0; i < imgs.length; i++) {
    var img = imgs[i];
    var src = img.currentSrc || img.src;
    if (src && !seen[src] && (img.width >= 80 || img.naturalWidth >= 80) && (img.height >= 80 || img.naturalHeight >= 80)) {
      seen[src] = true;
      count++;
      var a = document.createElement('a');
      a.className = 'bm-item';
      a.href = '#';
      var thumb = document.createElement('img');
      thumb.src = src;
      a.appendChild(thumb);
      a.onclick = (function(targetSrc){
        return function(e){
          e.preventDefault();
          container.remove();
          window.open('http://127.0.0.1:8000/images/create/?url=' + encodeURIComponent(targetSrc) + '&title=' + encodeURIComponent(document.title || 'Bookmarked Image'), '_blank');
        };
      })(src);
      imgList.appendChild(a);
    }
  }

  if (count === 0) {
    var emptyMsg = document.createElement('div');
    emptyMsg.className = 'bm-empty';
    emptyMsg.textContent = 'No images larger than 80x80px found on this page.';
    imgList.appendChild(emptyMsg);
  }
})();
