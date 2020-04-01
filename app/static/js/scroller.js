
function resize2() {
  var element = document.getElementById('width').offsetWidth;
  console.log(element)
  var newWidth = element/2;
  var el = document.getElementsByClassName('poster');
  var inf = document.getElementsByClassName('info');
  console.log(getComputedStyle(el[0]).getPropertyValue("-webkit-transform"))
  for(i = 0; i < el.length; i++) {
    el[i].style.webkitTransform = `translateZ(${newWidth}px)`;
    el[i].style.mozTransform = `translateZ(${newWidth}px)`;
    el[i].style.transform = `translateZ(${newWidth}px)`;
    inf[i].style.webkitTransform = `rotateY(90deg) translateZ(${newWidth}px)`;
    inf[i].style.mozTransform = `rotateY(90deg) translateZ(${newWidth}px)`;
    inf[i].style.transform = `rotateY(90deg) translateZ(${newWidth}px)`;
  }
  console.log(getComputedStyle(el[0]).getPropertyValue("-webkit-transform"))
  }

// inifinte scroller
var scroller = document.querySelector("#gifts");
var template = document.querySelector("#gifts-template");
var loaded = document.querySelector("#loaded");
var sentinels = {
                'gifts': document.querySelector("#sentinel"),
                "items": document.querySelector("#sentinelItems"),
                'boxes': document.querySelector("#sentinelBoxes")
                }
var counterGift = 0;
var inprogressGift = false;
var inprogressItem = false;
var inprogressBox = false;

function loadItemsGifts() {
  inprogressGift = true;
  fetch(`/loadGifts?c=${counterGift}`).then((response) => {
    response.json().then((data) => {
      
      for (var i = 0; i < data.length; i++) {
          let template_clone = template.content.cloneNode(true);
          template_clone.querySelector('#di').dataset.item = data[i][2];
          template_clone.querySelector('#is').src = "static/img/" + data[i][3]
          template_clone.querySelector('#is2').src = "static/img/" + data[i][7]
          template_clone.querySelector('#pid').id = data[i][0]
          // template_clone.querySelector('#pt').innerHTML = ""
          template_clone.querySelector('#pt2').innerHTML = data[i][1]
          template_clone.querySelector('#pd').innerHTML = data[i][6]
          template_clone.querySelector('#pp2').innerHTML = "$" + (Math.round(data[i][4] * 100) / 100).toFixed(2)
          // template_clone.querySelector('#pp2').innerHTML = "$" + (Math.round(data[i][4] * 100) / 100).toFixed(2)
          scroller.appendChild(template_clone);
          counterGift += 1;
          master(data[i][0]);

      }
      inprogressGift = false;
      resize2();
    })  
   
  })
  
}

var intersectionObserver = new IntersectionObserver(entries => {
  if (entries[0].intersectionRatio <= 0) {
    return;
  };
if (inprogressGift == false)

        {loadItemsGifts()};
        
    
});
intersectionObserver.observe(sentinels['gifts']);


var scrollerItem = document.querySelector("#items");
var templateItem = document.querySelector("#items-template");
var counterItem = 0;


function loadItemsItems() {
  inprogressItem = true;
  fetch(`/loadItems?c=${counterItem}`).then((response) => {
    response.json().then((data) => {
      for (var i = 0; i < data.length; i++) {
          let template_clone = templateItem.content.cloneNode(true);
          template_clone.querySelector('#di').dataset.item = data[i][2];
          template_clone.querySelector('#is').src = "static/img/" + data[i][3]
          template_clone.querySelector('#is2').src = "static/img/" + data[i][7]
          template_clone.querySelector('#pid').id = data[i][0]
          // template_clone.querySelector('#pt').innerHTML = ""
          template_clone.querySelector('#pt2').innerHTML = data[i][1]
          template_clone.querySelector('#pd').innerHTML = data[i][6]
          template_clone.querySelector('#pp2').innerHTML = "$" + (Math.round(data[i][4] * 100) / 100).toFixed(2)
          // template_clone.querySelector('#pp2').innerHTML = "$" + (Math.round(data[i][4] * 100) / 100).toFixed(2)
          scrollerItem.appendChild(template_clone);
          counterItem += 1;
          master(data[i][0]);
      }
      inprogressItem = false;
      resize2();
    })  
  })
}

var intersectionObserverItems = new IntersectionObserver(entries => {
  if (entries[0].intersectionRatio <= 0) {
    return;
  };
  if (inprogressItem == false){
  loadItemsItems();
  }
 
});
intersectionObserverItems.observe(sentinels['items']);

var scrollerBox = document.querySelector("#boxes");
var templateBox = document.querySelector("#boxes-template");
var counterBox = 0;

function loadItemsBoxes() {
  inprogressBox = true;
  fetch(`/loadBoxes?c=${counterBox}`).then((response) => {
    response.json().then((data) => {
      for (var i = 0; i < data.length; i++) {
          let template_clone = templateBox.content.cloneNode(true);
          template_clone.querySelector('#di').dataset.item = data[i][2];
          template_clone.querySelector('#is').src = "static/img/" + data[i][3]
          template_clone.querySelector('#is2').src = "static/img/" + data[i][7]
          template_clone.querySelector('#pid').id = data[i][0]
          template_clone.querySelector('#pt2').innerHTML = data[i][1]
          // template_clone.querySelector('#pt').innerHTML = ""
          template_clone.querySelector('#pd').innerHTML = data[i][6]
          template_clone.querySelector('#pp2').innerHTML = "$" + (Math.round(data[i][4] * 100) / 100).toFixed(2)
          // template_clone.querySelector('#pp2').innerHTML = "$" + (Math.round(data[i][4] * 100) / 100).toFixed(2)
          scrollerBox.appendChild(template_clone);
          counterBox += 1;
          master(data[i][0]);
      }
      inprogressBox = false;
      resize2();
    })  
  })
}


var intersectionObserverBoxes = new IntersectionObserver(entries => {

  if (entries[0].intersectionRatio <= 0) {
    return;
  };
  if (inprogressBox == false){
    loadItemsBoxes();
      }

});
intersectionObserverBoxes.observe(sentinels['boxes']);


$(window).resize(resize2() 
  );

$(function () {setInterval(resize2(), 1)})();