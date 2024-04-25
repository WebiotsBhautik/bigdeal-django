// $(document).ready(function () {
    let searchField = document.getElementById("changelist-search") || false;
    if (searchField) {
      let Table_options =
        document.querySelector(".change-list-actions .col-12") || false;
      Table_options && Table_options.appendChild(searchField);
      Table_options.classList.add("d-flex");
      Table_options.classList.add("justify-content-between");
    }
    
    // profilePicture-clear_id
    
    let profilePicCheckBox = document.getElementById("profilePicture-clear_id");
    if (profilePicCheckBox !== null && typeof profilePicCheckBox !== "undefined") {
      let lableForProfilePicCheckkBoxCheckbox = document.createElement("label");
      lableForProfilePicCheckkBoxCheckbox.setAttribute("for", "profilePicture-clear_id");
      lableForProfilePicCheckkBoxCheckbox.setAttribute("class", "toggle-btn");
      profilePicCheckBox.after(lableForProfilePicCheckkBoxCheckbox);
    }
    
    let isActiveCheckBox = document.getElementById("id_is_active");
    if (isActiveCheckBox !== null && typeof isActiveCheckBox !== "undefined") {
      let lableForIsActiveCheckbox = document.createElement("label");
      lableForIsActiveCheckbox.setAttribute("for", "id_is_active");
      lableForIsActiveCheckbox.setAttribute("class", "toggle-btn");
      isActiveCheckBox.after(lableForIsActiveCheckbox);
    }
    
    let isVendorCheckBox = document.getElementById("id_is_vendor");
    if (isVendorCheckBox !== null && typeof isVendorCheckBox !== "undefined") {
      let lableForIsVendorCheckbox = document.createElement("label");
      lableForIsVendorCheckbox.setAttribute("for", "id_is_vendor");
      lableForIsVendorCheckbox.setAttribute("class", "toggle-btn");
      isVendorCheckBox.after(lableForIsVendorCheckbox);
    }
    
    let isCustomerCheckBox = document.getElementById("id_is_customer");
    if (isCustomerCheckBox !== null && typeof isCustomerCheckBox !== "undefined") {
      let lableForIsCheckCheckbox = document.createElement("label");
      lableForIsCheckCheckbox.setAttribute("for", "id_is_customer");
      lableForIsCheckCheckbox.setAttribute("class", "toggle-btn");
      isCustomerCheckBox.after(lableForIsCheckCheckbox);
    }
    
    $(document).ready(function () {
      // Run when page is load or refresh
      var dropdown = $("#id_productType");
      var dropdownValue = dropdown.val();
      var productTabAreaControlValue = "product-tab";
    
      var productTabElement = document.querySelector("[aria-controls='" + productTabAreaControlValue + "']");
      console.log("dropdownValue dropdownValue dropdownValue ====>",dropdownValue)
      if(dropdownValue==""){
        productTabElement.classList.add("d-none");
      }
      if(dropdownValue=="Simple" || dropdownValue=="Classified"){
        productTabElement.classList.remove("d-none");
        
        var addAnother = document.getElementsByClassName("btn btn-sm btn-default float-right");
        if(dropdownValue=="Simple"){
          var productFormGroup = document.getElementById('product-tab');
          var productForms = productFormGroup.getElementsByClassName("panel inline-related has_original dynamic-productvariant_set");
    
          // =================================================================
          var productFormsRelatedDynamic = productFormGroup.getElementsByClassName("panel inline-related dynamic-productvariant_set");
          if(productFormsRelatedDynamic[0]){
            var attributeElementOfRelatedForm = productFormsRelatedDynamic[0].getElementsByClassName("form-group field-productVariantAttribute");
            if(attributeElementOfRelatedForm[0]){
              attributeElementOfRelatedForm[0].classList.add("d-none");
            }
          }
          // =================================================================
    
          if(productForms[0]){
            var attributeElement = productForms[0].getElementsByClassName("form-group field-productVariantAttribute");
            attributeElement[0].classList.add("d-none");
          }
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // Hiding delete checkbox
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          if(productForms[0]){
            var deleteCheckBoxElement = productForms[0].getElementsByClassName("card-tools delete");
            if(deleteCheckBoxElement[0]){
              deleteCheckBoxElement[0].classList.add("d-none");
            }
          }
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
          // ---------------------------------------------------------------------------------------------
          for (var i = productForms.length; i > 0; i--) {
            if (productForms[i] !== null &&
              typeof productForms[i] !== "undefined")
              {
              // var deleteCheckbox = productForms[i].getElementsByClassName("vCheckboxLabel inline");
              var deleteCheckbox = productForms[i].querySelector('input[type=checkbox]')
              console.log('deleteCheckbox.checked ===>',deleteCheckbox.checked);
              if(deleteCheckbox.checked){
                productForms[i].classList.add("d-none");
              }
            }
              
          }
    
          // ---------------------------------------------------------------------------------------------
    
          setTimeout(() => {
            if(addAnother[0])
            {
              addAnother[0].classList.add("d-none");
            }
          }, 200);
        }
        if(dropdownValue=="Classified"){
    
          var productFormGroup = document.getElementById('product-tab');
          var productForms = productFormGroup.getElementsByClassName("panel inline-related has_original dynamic-productvariant_set");
    
          // =================================================================
          var productFormsRelatedDynamic = productFormGroup.getElementsByClassName("panel inline-related dynamic-productvariant_set");
          if(productFormsRelatedDynamic[0]){
            var attributeElementOfRelatedForm = productFormsRelatedDynamic[0].getElementsByClassName("form-group field-productVariantAttribute");
            if(attributeElementOfRelatedForm[0]){
              attributeElementOfRelatedForm[0].classList.remove("d-none");
            }
          }
          // =================================================================
    
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          // Hiding delete checkbox
          // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
          if(productForms[0]){
            var deleteCheckBoxElement = productForms[0].getElementsByClassName("card-tools delete");
            if(deleteCheckBoxElement[0]){
              deleteCheckBoxElement[0].classList.add("d-none");
            }
          }
         
    
          if(productForms[0])
          {
            var attributeElement = productForms[0].getElementsByClassName("form-group field-productVariantAttribute");
            attributeElement[0].classList.remove("d-none");
          }
          setTimeout(() => {
            if(addAnother[0])
            {
              addAnother[0].classList.remove("d-none");
            }
          }, 200);
        }
      }
    
    
    
      // Run when user change Product Type by clicking on the Product Type dropdown
      function updateInlines() {
        var selectedValue = dropdown.val();
         
        if(selectedValue==""){
          productTabElement.classList.add("d-none");
        }
    
        if(selectedValue=="Simple" || selectedValue=="Classified"){
          productTabElement.classList.remove("d-none");
    
          var addAnother = document.getElementsByClassName("btn btn-sm btn-default float-right");
    
          // When dropdown value seted to Simple
          if(selectedValue=="Simple"){
              if(addAnother[0])
              {
                addAnother[0].classList.add("d-none");
              }
              var productFormGroup = document.getElementById('product-tab');
              var productRmvBtns= productFormGroup.getElementsByClassName("inline-deletelink");
              var productForms = productFormGroup.getElementsByClassName("panel inline-related has_original dynamic-productvariant_set");
              var productFormsRelated = productFormGroup.getElementsByClassName("panel inline-related last-related dynamic-productvariant_set");
    
              // =================================================================
              var productFormsRelatedDynamic = productFormGroup.getElementsByClassName("panel inline-related dynamic-productvariant_set");
              if(productFormsRelatedDynamic[0]){
                var attributeElementOfRelatedForm = productFormsRelatedDynamic[0].getElementsByClassName("form-group field-productVariantAttribute");
                if(attributeElementOfRelatedForm[0]){
                  attributeElementOfRelatedForm[0].classList.add("d-none");
                }
              }
              // =================================================================
              
    
              for (var i = productRmvBtns.length; i > 0; i--) {
                if (
                  productRmvBtns[i] !== null &&
                  typeof productRmvBtns[i] !== "undefined"
                ){
                  productRmvBtns[i].click();
                }
                  
              }
    
              for (var i = productForms.length; i > 0; i--) {
                if (productForms[i] !== null &&
                  typeof productForms[i] !== "undefined")
                  {
      
                  var deleteCheckbox = productForms[i].getElementsByClassName("vCheckboxLabel inline");
                  for (var j = deleteCheckbox.length; j >= 0; j--) {
                    if (
                      deleteCheckbox[j] !== null &&
                      typeof deleteCheckbox[j] !== "undefined"
                    ) {
                      deleteCheckbox[j].click();
                    }
                  }
                  productForms[i].classList.add("d-none");
                }
                  
              }
    
              // ============================================================
              for (var i = productFormsRelated.length; i >= 0; i--) {
                if (productFormsRelated[i] !== null &&
                  typeof productFormsRelated[i] !== "undefined")
                  {
      
                  var rmvBtn = productFormsRelated[i].getElementsByClassName("inline-deletelink");
                  for (var j = rmvBtn.length; j >= 0; j--) {
                    if (
                      rmvBtn[j] !== null &&
                      typeof rmvBtn[j] !== "undefined"
                    ) {
                      rmvBtn[j].click();
                    }
                  }
                }
                  
              }
              // ============================================================
    
    
            
    
              setTimeout(() => {
              if(productForms[0]){
              var attributeElement = productForms[0].getElementsByClassName("form-group field-productVariantAttribute");
    
                var quantityElement=document.getElementById('id_productvariant_set-0-productVariantQuantity');
                var priceElement=document.getElementById('id_productvariant_set-0-productVariantPrice');
                var discountElement=document.getElementById('id_productvariant_set-0-productVariantDiscount');
                var taxElement=document.getElementById('id_productvariant_set-0-productVariantTax');
                
                if(attributeElement[0]){
                  attributeElement[0].classList.add("d-none");
                }
                quantityElement.value="";
                priceElement.value="";
                discountElement.value="";
                taxElement.value="";
              }
            },200);
          
            // id_productvariant_set-0-productVariantAttribute
            // id_productvariant_set-0-productVariantQuantity
            // id_productvariant_set-0-productVariantPrice
            // id_productvariant_set-0-productVariantDiscount
            // id_productvariant_set-0-productVariantTax
          }
    
          // When dropdown value seted to Classified
          if(selectedValue=="Classified"){
            var productFormGroup = document.getElementById('product-tab');
            var productForms = productFormGroup.getElementsByClassName("panel inline-related has_original dynamic-productvariant_set");
    
            // =================================================================
            
            var productFormsRelated = productFormGroup.getElementsByClassName("panel inline-related dynamic-productvariant_set");
            if(productFormsRelated[0]){
            var attributeElementOfRelatedForm = productFormsRelated[0].getElementsByClassName("form-group field-productVariantAttribute");
            if(attributeElementOfRelatedForm[0]){
              attributeElementOfRelatedForm[0].classList.remove("d-none");
            }
            }
            // =================================================================
    
            if(productForms[0]){
              var attributeElement = productForms[0].getElementsByClassName("form-group field-productVariantAttribute");
              attributeElement[0].classList.remove("d-none");
            }
    
              if(addAnother[0])
              {
                addAnother[0].classList.remove("d-none");
              }
    
              var productFormGroup = document.getElementById('product-tab');
              var productForms = productFormGroup.getElementsByClassName("panel inline-related has_original dynamic-productvariant_set");
              for (var i = productForms.length; i > 0; i--) {
                if (
                  productForms[i] !== null &&
                  typeof productForms[i] !== "undefined"
                ){
      
                  var deleteCheckbox = productForms[i].getElementsByClassName("vCheckboxLabel inline");
                  for (var j = deleteCheckbox.length; j >= 0; j--) {
                    if (
                      deleteCheckbox[j] !== null &&
                      typeof deleteCheckbox[j] !== "undefined"
                    ) {
                      deleteCheckbox[j].click();
                    }
                  }
                  productForms[i].classList.remove("d-none");
                }
                  
              }
    
              
          }
        }
      }
    
      dropdown.change(function () {
        updateInlines();
      });
    });


// ====================================================================================

document.addEventListener('DOMContentLoaded', function() {
  // Get the main-sidebar element
  var mainSidebar = document.getElementById('jazzy-sidebar');

  // Get all the menu items within the main-sidebar
  var menuItems = mainSidebar.querySelectorAll('a');

  // Add a click event listener to each menu item
  menuItems.forEach(function(item) {
    item.addEventListener('click', function(event) {
      // Get the active menu item
      var activeMenuItem = mainSidebar.querySelector('.active');

    });
  });
});




setTimeout(function () {
  $('#error-message').fadeOut('slow')
}, 6000)


  
    