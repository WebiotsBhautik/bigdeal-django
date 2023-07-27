/*=====================  
 range slide
 ==========================*/

 $(function () {
   var params = new URLSearchParams(window.location.search);
   min = Number(document.getElementById('filter-price-range').getAttribute('min')) || 0,
   max = Number(document.getElementById('filter-price-range').getAttribute('max')) || 0,
   prefix = document.getElementById('filter-price-range').getAttribute('prefix')
   var PriceArray = params.get('price')?params.get('price').split(','):[min,max];


    $(".js-range-slider").ionRangeSlider({
       type: "double",
        grid: true,
        min: min,
        max: max,
        from: PriceArray[0],
        to: PriceArray[1],
        prefix: prefix,
    });
   });
 