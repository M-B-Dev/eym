// show/hide cart and modal
(function(){
  $(".hide").hide();

  const cartInfo = document.getElementById('cart-info');
  var modal = document.getElementById('cartModal');
  const cart = document.getElementById('cart');
  window.addEventListener('click', function(e){
    if(e.target == modal){
      modal.classList.toggle('show-modal');
      cart.classList.toggle('show-cart');
      }
    }
  );
  cartInfo.addEventListener('click', function(e){
    cart.classList.toggle('show-cart');
    modal.classList.toggle('show-modal');
    $.getJSON('/update_cart', function (data) {
      updateCart(data)
      }
    );
  })

})();

// update cart
function updateCart(data) {
  if (data.lang == "es") {
    price = "Precio";
    qty = "Candidad";
    clear = "Vaciar Carrito";
  } 
  else {
    price = "Price";
    qty = "Quantity";
    clear = "Clear Cart";
  }
    $('.item-total').html(
      (Math.round(data.total * 100) / 100).toFixed(2)
      );
    if (data.total_products == 1 ){
      $('.total-products').html(data.total_products + '\xa0' + 'item - $');
    }
    else if (data.total_products > 1 ) {
      $('.total-products').html(data.total_products + '\xa0' + 'items - $');
    }
    else if (data.total_products < 1) {
      $('.total-products').html(data.total_products + '\xa0' + 'items - $');
    }
    var arrayLength = data.items.length;
    div = document.getElementById('items-cart');
    div.innerHTML = ""
    for (var i = 0; i < arrayLength; i++){
      div.insertAdjacentHTML( 'beforeend', `
        <div class='cart-item d-flex justify-content-between text-capitalize my-3'>
          <img src="static/img-cart/` + data.items[i][2] + `" class="img-fluid rounded-circle" id="item-img" alt="">
          <div class="item-text">
            <p id="cart-item-title" class="font-weight-bold mb-0">` + data.items[i][1] + `</p>
            <span id="cart-item-price" class="cart-item-price" class="mb-0">${price}: ` + (Math.round(data.items[i][0] * 100) / 100).toFixed(2) + ` | </span>
            <span id="cart-item-price" class="cart-item-price" class="mb-0">${qty}:` + data.items[i][4] + `</span>
          </div>
          <a href="#" id='trash-` + i + `' class="cart-item-remove">
          <i class="fas fa-trash"></i>
          </a>
        </div>`
        );
      // remove item
      (function () {
        var index = i;
          $(`a#trash-` + index).bind('click', function() {
            $.getJSON('/remove_item',
                {I: index},
                function(data){updateCart(data)});
                return false;
              });
            })();
      };
    if (data.total_products > 0 ){
      $('#buttons-cart').html(` 
        <div class="cart-total-container d-flex justify-content-around text-capitalize mt-5">
          <h4>total</h4>
          <h4> $ <strong id="cart-total" class="font-weight-bold">`
            + (Math.round(data.total * 100) / 100).toFixed(2) +
          `</strong> </h4>
        </div>
        <div class="row padding" class="store-items" id="store">
          <a href="index/clear" id="clear-cart" class="btn btn-outline-secondary btn-black text-uppercase">${clear}</a>
          <a href="/checkout" class="btn btn-outline-secondary text-uppercase btn-pink">Checkout</a>

        </div>`
      );
    }
  else {
    $('#buttons-cart').html(` 
      <div class="cart-total-container d-flex justify-content-around text-capitalize mt-5">
        <h5>total</h5>
        <h5> $ <strong id="cart-total" class="font-weight-bold">`
          + (Math.round(data.total * 100) / 100).toFixed(2) +
        `</strong> </h5>
      </div>`
    );
  };
};

// button functionality for adding items to cart
function master(product) {
    $('a#' + product).bind('click', function addToCart() {
      $.getJSON('/add_item',
          {product_id: product},
          function (data) {
            updateCart(data)
          }
        );
      return false;
    });
  };


