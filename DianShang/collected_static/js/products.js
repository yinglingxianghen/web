jQuery(function($) {
	
	/*
	| ----------------------------------------------------------------------------------
	| Shopping cart - Remove Row on click Close button
	| ----------------------------------------------------------------------------------
	*/

	$('.add-cart').on('click', function() {
		var product_id = $(this).data('product-id');
		var qty=$('#id_quantity option:selected') .val();
		if (qty==null){
			qty=1;
		}
		var var_data = {
                'csrfmiddlewaretoken':$("input[name='csrfmiddlewaretoken']").val(),
                'product_id':product_id,
			    'quantity' :qty,
            }
         var url='/addcart/';
         $.ajax({
                url:url ,
                type: "POST",
                data: var_data,
                cache: false,
                dataType: 'json',
                success: function (data) {
					if (data.status == "200") {
						alert('成功加入购物车');
						window.location.reload();
					}
					else{
						alert('系统错误，请与管理员联系');
					}
				}	
			});
	});
	
	
	
	
	/*
	| ----------------------------------------------------------------------------------
	| Product Single Page - Change Product Preview Image
	| ----------------------------------------------------------------------------------
	*/
	$('.product-preview .thumbs > li > a').on('click', function(e) {
		e.preventDefault();
		var $preview = $('.product-preview .big-image');
		$preview.find('a').attr( 'href', $(this).attr('href') );
		$preview.find('img').attr( 'src', $(this).children().attr('src') );
	});
	
	
	/*
	| ----------------------------------------------------------------------------------
	| Setup Product Grid Layout
	| ----------------------------------------------------------------------------------
	*/
	var $product_layout = $('.products-layout');
	
	function setupProduct() {
		var itemW = 270,
			productW = $product_layout.width();
		
		x = parseInt(productW / itemW);
		var new_itemW = parseInt(productW / x).toString() + 'px';
		if ( x == 1 ) 
		{
			new_itemW = '100%';
		}
		$product_layout.find('.product').each(function() {
			var $this = $(this), added_classes = '';
			
			$this = ( ! $this.parent().hasClass('mix-item') ) ? $this.wrap('<div class="mix-item ' + added_classes + '" />').parent() : $this.parent();
			$this.children().css('visibility', 'visible');
			
			var $lazyLoad = $this.find('.lazyLoad');
			if ( $lazyLoad.length )
			{
				$this.addClass('loading');
			}
			
			$this.css({
				'width': new_itemW
			});
			$this.children().animate({
				opacity: 1,
				visibility: 'visible'
			}, 800, 'easeInQuad');
			
			$lazyLoad.attr( 'src', $lazyLoad.data('src') ).imagesLoaded(function() {
				$lazyLoad.removeAttr('data-src');
				$this.removeClass('loading');
			});
		});
	}
	
	if ( $product_layout.length )
	{
		setupProduct();
		
		$product_layout.imagesLoaded(function() {
			$product_layout.isotope({
				itemSelector: '.mix-item'
			});
		});
		
		$(window).smartresize(function() {
			setupProduct();
		});
	}
	

	$('[data-layout="list"], [data-layout="grid"]').on('click', function(e) {
		e.preventDefault();
		$product_layout.toggleClass('grid').toggleClass('list').isotope('reLayout');
		$(this).closest('ul').find('.active').removeClass('active');
		$(this).addClass('active');
	});
	
	
	/*
	| ----------------------------------------------------------------------------------
	| Isotope Filter - Filter by Category and Brands
	| ----------------------------------------------------------------------------------
	*/
	filterCheckbox( $('#category-list'), 'category' );
	filterCheckbox( $('#brands-list'), 'brand' );
	filterCheckbox( $('#filter-by-color'), 'colors' );
	filterCheckbox( $('#filter-by-size'), 'size' );
	
	function filterCheckbox($container, type)
	{
		$container.find('input[type="checkbox"]').on('change', function() {
			var filters = [];
			$container.find('input[type="checkbox"]:checked').each(function() {
				this_filter = $(this).val();
				if ( filters.indexOf(this_filter) === -1 && this_filter !== undefined )
				{
					filters.push(this_filter);
				}
			});
			
			
			var products = $product_layout.find('.mix-item').filter(function() {
				if ( filters.length == 0 ) return true;
				var $this = $(this),
					filter = $this.find(' > .product').data(type),
					filter_arr;
				
				if ( filter !== undefined )
				{
					filter_arr = filter.split('|');
					for ( var i = 0; i < filter_arr.length; i++ )
					{
						if ( filters.indexOf(filter_arr[i]) !== -1 ) return true;
					}
					return false;
				}
			});
			
			$product_layout.isotope({
				filter: products
			});
		});
	}
	
	
	/*
	| ----------------------------------------------------------------------------------
	| Isotope Filter - Filter by Price
	| ----------------------------------------------------------------------------------
	*/
	function priceSlider(value)
	{
		var products = $product_layout.find('.mix-item').filter(function() {
			var price = $(this).find(' > .product').data('price');
			if ( price === undefined ) return false;
			return ( price >= value[0] && price < value[1] ) ? true : false;
		});
		
		$product_layout.isotope({
			filter: products
		});
	}
	
	
	/*
	| ----------------------------------------------------------------------------------
	| Set input value of filters
	| ----------------------------------------------------------------------------------
	*/
	$('#filter-by-size li > a, #filter-by-color li > a').on('click', function(e) {
		e.preventDefault();
		var $this = $(this);
		$this.toggleClass('active');
		$this.siblings('.filter-checkbox').prop( 'checked', $this.hasClass('active') ).trigger('change');
	});
	
	
	/*
	| ----------------------------------------------------------------------------------
	| Add Helper Classes to Vertical Menu
	| ----------------------------------------------------------------------------------
	*/
	$('.vmenu li').each(function() {
		if ( $(this).find('ul').length )
		{
			$(this).addClass('has-submenu');
		}
	});
	

	/*
	| ----------------------------------------------------------------------------------
	| jQuery Range slider - noUiSlider
	| Git: https://github.com/leongersen/noUiSlider
	| URL: http://refreshless.com/nouislider/
	| ----------------------------------------------------------------------------------
	*/
	$('.range-slider').each(function() {
		var $this = $(this),
			configs = new Array();
		
		configs['min'] = ( $this.data('min') === undefined ) ? 0 : $this.data('min');
		configs['max'] = ( $this.data('max') === undefined ) ? 100 : $this.data('max');
		configs['start'] = ( $this.data('start') === undefined ) ? [configs['min'], configs['max']] : $this.data('start');
		configs['step'] = ( $this.data('step') === undefined ) ? 1 : $this.data('step');
		configs['currency'] = ( $this.data('currency') === undefined ) ? '$' : $this.data('currency');
		
		$this.noUiSlider({
			range: [configs['min'], configs['max']],
			start: configs['start'],
			step: configs['step'],
			connect: true,
			handles: 2,
			slide: function() {
				var values = $(this).val();
					
				$this.siblings('.range-slider-value').find('> .min').text( configs['currency'] + values[0] );
				$this.siblings('.range-slider-value').find('> .max').text( configs['currency'] + values[1] );
			},
			serialization: {
				to: [ 'min-price', 'max-price' ],
				resolution: 1,
				mark: ","
			},
		}).change(function() { priceSlider( $(this).val() ); });
		
		$this.siblings('.range-slider-value').find('> .min').text( configs['currency'] + $this.val()[0] );
		$this.siblings('.range-slider-value').find('> .max').text( configs['currency'] + $this.val()[1] );
	});

});