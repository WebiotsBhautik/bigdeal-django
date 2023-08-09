

/*=====================
  timer js
 ==========================*/
(function($) {
    "use strict";

    function updateCountdown(){

    //    Set the date we're counting down to
        var currentDate = new Date();
        var countDownDate = new Date(currentDate);
        countDownDate.setDate(countDownDate.getDate() + 12); // Adding 12 days to the current date

        
    //    Update the count down every 1 second
        var x = setInterval(function() {
            var now = new Date().getTime();  // Get todays date and time
            var distance = countDownDate - now;  // Find the distance between now an the count down date

            // Time calculations for days, hours, minutes and seconds
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);


            // Output the result in an element with id="demo"
            document.getElementById("demo").innerHTML =
                "<span>" + days + "<span class='timer-cal'>Days</span></span>" +
                "<span>" + hours + "<span class='timer-cal'>Hrs</span></span>" +
                "<span>" + minutes + "<span class='timer-cal'>Min</span></span>" + 
                "<span>" + seconds + "<span class='timer-cal'>Sec</span></span> ";   


            // If the count down is over, write some text
            if (distance < 0) {
                clearInterval(x);
                updateCountdown(); // Restart the countdown with a new 12-day interval
                // document.getElementById("demo").innerHTML = "EXPIRED";
            }
        }, 1000);
        }

           // Initial call to start the countdown
    updateCountdown();
})(jQuery);







