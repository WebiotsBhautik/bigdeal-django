async function searchValue(){
query = document.getElementById('search-input').value;
document.getElementById("search-input").innerHTML = "You search: " + query;
console.log('query ==========>',query)

response = await fetch(`/search_products/?q=${query}&category={{theme}}`);

productData = await response.json();
}