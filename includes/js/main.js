window.onload=function(){
style();
}

function style(){
  document.getElementById("map_d").style.display="block";
  document.getElementById("map_e").style.display="block";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("l0").style.display="block";
  document.getElementById("l1").style.display="block";
  document.getElementById("l2").style.display="block";
  document.getElementById("l3").style.display="block";
  document.getElementById("l4").style.display="block";
  document.getElementById("l5").style.display="block";
  document.getElementById("animation").style.display="block";
}

function map_d(){
  document.getElementsByClassName("mapcontainer")[0].style.display="none";
  document.getElementById("map_d").style.display="none";
  document.getElementById("map_e").style.display="block";
  document.getElementById("map_e").style.background="green";
  const elements=document.getElementsByClassName("1");
  for (const element of elements){
    element.style.display="none";
  }
}

function map_e(){
  document.getElementsByClassName("mapcontainer")[0].style.display="block";
  document.getElementById("map_e").style.display="none";
  document.getElementById("map_d").style.display="block";
  document.getElementById("map_d").style.background="red";
  const elements=document.getElementsByClassName("1");
  for (const element of elements){
    element.style.display="block";
  }
}

function mapl_d(){
  const elements=document.getElementsByTagName("svg");
  for (const element of elements){
    element.style.display="none";
  }
  document.getElementById("mapl_d").style.display="none";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("mapl_e").style.background="green";
}

function mapl_e(){
  const elements=document.getElementsByTagName("svg");
  for (const element of elements){
    element.style.display="block";
  }
  document.getElementById("mapl_e").style.display="none";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_d").style.background="red";
}

function mapl_d(){
  const elements=document.getElementsByTagName("svg");
  for (const element of elements){
    element.style.display="none";
  }
  document.getElementById("mapl_d").style.display="none";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("mapl_e").style.background="green";
}

function mapl_e(){
  const elements=document.getElementsByTagName("svg");
  for (const element of elements){
    element.style.display="block";
  }
  document.getElementById("mapl_e").style.display="none";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_d").style.background="red";
}

function l0_d(){
  document.getElementById("layer0").style.display="none";
  document.getElementById("mapl_d").style.display="none";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("mapl_e").style.background="green";
}

function l0_e(){
  document.getElementById("layer0").style.display="block";
  document.getElementById("mapl_e").style.display="none";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_d").style.background="red";
}

function l1_d(){
  document.getElementById("layer1").style.display="none";
  document.getElementById("mapl_d").style.display="none";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("mapl_e").style.background="green";
}

function l1_e(){
  document.getElementById("layer1").style.display="block";
  document.getElementById("mapl_e").style.display="none";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_d").style.background="red";
}

function l2_d(){
  document.getElementById("layer2").style.display="none";
  document.getElementById("mapl_d").style.display="none";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("mapl_e").style.background="green";
}

function l2_e(){
  document.getElementById("layer2").style.display="block";
  document.getElementById("mapl_e").style.display="none";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_d").style.background="red";
}

function l3_d(){
  document.getElementById("layer3").style.display="none";
  document.getElementById("mapl_d").style.display="none";
  document.getElementById("mapl_e").style.display="block";
  document.getElementById("mapl_e").style.background="green";
}

function l3_e(){
  document.getElementById("layer3").style.display="block";
  document.getElementById("mapl_e").style.display="none";
  document.getElementById("mapl_d").style.display="block";
  document.getElementById("mapl_d").style.background="red";
}

function animation(){
  document.getElementById("layer1").style.display="none";
  document.getElementById("layer2").style.display="none";
  document.getElementById("layer3").style.display="none";
  document.getElementById("layer4").style.display="none";
for (let i=0; i<10;i++){
  setTimeout(() => document.getElementById("layer0").style.display="block",1000);
  setTimeout(() => document.getElementById("layer0").style.display="none",1500);
  setTimeout(() => document.getElementById("layer1").style.display="block",1500);
  setTimeout(() => document.getElementById("layer1").style.display="none",2000);
  setTimeout(() => document.getElementById("layer2").style.display="block",2000);
  setTimeout(() => document.getElementById("layer2").style.display="none",4000);
  setTimeout(() => document.getElementById("layer1").style.display="block",4000);
  setTimeout(() => document.getElementById("layer1").style.display="none",6000);
  setTimeout(() => document.getElementById("layer0").style.display="block",6000);
  }
}

function debug(){
$.ajax({
  url: "debug.html",
  cache: false
  }).done(function(data){
  $(".debug").html(data);
  });
}

function info(link){
$.ajax({
  url: "info/buildings/"+link,
  cache: false
  }).done(function(data){
  $(".info").html(data);
  });
}

