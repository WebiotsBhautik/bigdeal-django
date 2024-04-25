window.onload = function(){
    let themeslider   = document.querySelector('.home-slide'),
        elemOne   = document.querySelector('#img-1');
        // elemTwo   = document.querySelector('#img-2'),
        // elemThree   = document.querySelector('#img-3');

    themeslider.addEventListener('mousemove',function(e){
        var pageX = e.clientX - window.innerWidth/1,
            pageY = e.clientY - window.innerHeight/1;
            elemOne.style.transform = 'translateX(' + (7 + pageX/150) + '%) translateY(' + (1 + pageY/150) + '%)';
            // elemTwo.style.transform = 'translateX(' + (7 + pageX/150) + '%) translateY(' + (1 + pageY/150) +  '%)';
            // elemThree.style.transform = 'translateX(' + (7 + pageX/150) + '%) translateY(' + (1 + pageY/150) +  '%)';
        });
    };


    // let query
    // async function searchValue() {
    //   query = document.getElementById("search-input").value;
    //   document.getElementById("search-input").innerHTML = "you search :" + query;
    //   console.log('query ==========+>',query);

    // const response = await fetch(`/search_products/?q=${query}&category={{theme}}`);

    //   const productData = await response.json();
    //   displayProductData(productData);
    //   console.log('productData ==========+>',productData);
    // }

    //   function displayProductData(productData) {
    //   $("#realData").empty();

    //   if(productData.data.length === 0){
    //     $('#realData').append('<li class="no-results"> No products found! </li>');
    //     return;
    //   }
      
    //   productData.data.map(value => {
    //     let ratingHtml = '';
    //     if (parseInt(value.rating) < 5) {
    //       for (let i = 0; i < parseInt(value.rating); i++) {
    //         ratingHtml += '<li><a class="fa fa-star theme-color" id="productOfStar" href="/product-detail/' + value.id + '"></a></li>';
    //       }
    //       let emptyStars = 5 - parseInt(value.rating);
    //       for (let i = 0; i < emptyStars; i++) {
    //         ratingHtml += '<li><i class="fa fa-star"></i></li>';
    //       }
    //     } else {
    //       for (let i = 0; i < 5; i++) {
    //         ratingHtml += '<li><a class="fa fa-star theme-color" id="productOfStar" href="/product-detail/' + value.id + '"></a></li>';
    //       }
    //     }
    //     $("#realData").append(`<li>
    //       <div class="product-cart media">
    //         <a href="/product-detail/${value.id}">
    //           <img
    //             src="${value.image_url}"
    //             href="/product-detail/${value.id}"
    //             class="img-fluid blur-up lazyload"
    //             alt=""
    //           />
    //         </a>

    //         <div class="media-body">
    //           <a href="/product-detail/${value.id}">
    //             <h6 class="mb-1">${value.name}</h6>
    //           </a>
    //           <ul class="rating p-0">
    //             ${ratingHtml}
    //           </ul>
    //           <a href="/product-detail/${value.id}" class="mb-0 mt-1">$${value.price}</a>
    //         </div>
    //       </div>
    //   </li>`)
    //   });
    // }








