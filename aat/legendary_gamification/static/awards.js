function reload(){
    var container = document.getElementById("user-leaderboard");
    var content = container.innerHTML;
    container.innerHTML= content; 
    
   //this line is to watch the result in console , you can remove it later	
    console.log("Refreshed"); 
}

while (true) {
    setTimeout(reload(), 1000);
}