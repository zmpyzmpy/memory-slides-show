var uid = 'adslkfa';
var stories = [];
function load_slide(){
  url = "http://0.0.0.0:8000/slideshow?u_id=".concat(uid);
  console.log(url);
  $.ajax({
    url: url,
    cache: false,
    method: "GET",
    crossDomain:true
  })
  .done(function(tweets) {
    window.location.href='./slideshow.html';
    localStorage.setItem("tweets",JSON.stringify(tweets));
  });


}

function show_slide(){
  var slide_ul = document.getElementById("slide_ul");
  slide_ul.innerHTML = "";
  tweets = JSON.parse(localStorage.getItem("tweets"));
  console.log(tweets);
  stories = [];
  for (var i in tweets) {
    if (tweets[i]["replies"].length==0){
      // stories.push({});
      //
      // stories[stories.length-1]["text"] = tweets[i]["tweet"];
      // stories[stories.length-1]["img"] = tweets[i]["img"];
      continue;
    }
    for (var j in tweets[i]["replies"]){
      stories.push({});

      stories[stories.length-1]["text"] = tweets[i]["tweet"];
      stories[stories.length-1]["img"] = tweets[i]["img"];
      reply = tweets[i]["replies"][j];
      $("#slide_ul").append('<li>                <div class="twitter-user">\
                        <img class="profile-icon" src="../app/'+reply["profile"] +'"/>\
                        <text class="screen-name">'+reply["user_name"]+'</text>\
                      </div>\
                      <img class="slide-img" src="../app/'+reply["img"]+'"/>\
                      <div class="twitter-content">\
                      '+reply["text"] +'\
                      </div>\
                      </li>');
    }
  }
  return stories;
}
function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
}
uid = getURLParameter('id');
function load_presentation(){
  setTimeout(function() {
    load_slide();
  }, 3000);

  url = "http://0.0.0.0:8000/all_pics?u_id=".concat(uid);
  $.ajax({
    url: url,
    cache: false,
    method: "GET",
    crossDomain:true
  })
  .done(function( pics ) {
    var img_gallery = document.getElementById("img_gallery");
    img_gallery.innerHTML = "";
    for (i=0;i<pics.length;i++){
      $("#img_gallery").append('        <div class="floated_img">\
                <img class="img_" id="zmpy" src="../app'+ pics[i] +'">\
            </div>');

    }
  });
  setTimeout(function() {
    test();
  }, 100);
}

function test(){
  imgs = document.getElementsByClassName("img_");
  for (i=0;i<imgs.length;i++){
    imgs[i].addEventListener('click', function (){
      document.getElementById("enlarge_img").src = this.src;
      // console.log(this.src);
    });
  }
}
