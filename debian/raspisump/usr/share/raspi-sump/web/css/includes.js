// includes.js
function fetchInclude(url, elementId) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var responseText = this.responseText;
        document.getElementById(elementId).innerHTML = responseText;
      }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
  }
