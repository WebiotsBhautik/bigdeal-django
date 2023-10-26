(function($) {
    "use strict";
    $(window).on('load', function() {
        if ($('#exampleModal').length) {

        $('#exampleModal').modal('show');
        }else{
            $('#search-input').focus();
        }
    });

    $('#exampleModal').on('hidden.bs.modal', function () {
        $('#search-input').focus();
      });

    function openSearch() {
        document.getElementById("search-overlay").style.display = "block";
    }

    function closeSearch() {
        document.getElementById("search-overlay").style.display = "none";
    }
  
})(jQuery);

  function dismiss(){
    document.getElementById('dismiss').style.display='none';
};