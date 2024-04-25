// Handle Checkout Function Start ============================================================

// Handle coupon validation start ===========================>

// Add a click event listener to the button

var couponBtn = document.getElementById('couponBtn');
couponBtn.addEventListener('click',function(){

  // Get the coupon code value
  const couponCode = document.getElementById('couponCode').value;

  // Create a new AJAX request
  const xhr = new XMLHttpRequest();

  // Configure the request
  xhr.open('POST','/validate_coupon/'); // Replace '/validate_coupon/' with the URL of your Django view that validates the coupon
  xhr.setRequestHeader('Content-Type','application/json');

  // Define the data to be sent
  const data = JSON.stringify({couponCode});

  // Handle the AJAX response
  xhr.onreadystatechange = function(){
    if(xhr.readyState === XMLHttpRequest.DONE){
      const billingAddressDiv = document.querySelector("#billingAddressDiv");
      if(xhr.status === 200){
        // Process the response
        const response = JSON.parse(xhr.responseText);
        if(response.valid){
          billingAddressDiv.style.display = "block";
        }
      }else{
        console.error('AJAX request failed');
      }
    }
  };

  // Send the AJAX request
  xhr.send(data);
});

// Handle coupon validation end =========================>



// <============= Add a click event listener to the button ===================>

var couponBtn = document.getElementById('couponBtn');
const billingAddressDiv = document.querySelector("#billingAddressDiv");
couponBtn.addEventListener('click',function(){
  // Get the coupon code value
  const couponCode = document.getElementById('couponCode').value;

  var url = "{% url 'validate_coupon' %}";

  fetch (url,{
    method: "POST",
    headers: {
      "Content-type":"application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      couponCode: couponCode,
    }),
  })
  .then((response) => response.json())
  .then((data) => {
    if(data.valid === "True"){
      billingAddressDiv.style.display = "block";
    }
    if(data.valid === "False"){
      billingAddressDiv.style.display = "none";
    }
  });
});
