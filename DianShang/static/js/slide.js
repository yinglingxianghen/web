/**
 * 首页轮播图JS
 */
$(function(){
	var numpic = $('#slidelist li').size()-1;
	var nownow = 0;
	var inout = 0;
	var TT = 0;
	var SPEED = 5000;


	$('#slidelist li').eq(0).siblings('li').css({'display':'none'});


	var ulstart = '<ul id="pagination" style="margin-left: -68px;">',
		ulcontent = '',
		ulend = '</ul>';
	ADDLI();
	var pagination = $('#pagination li');
	var paginationwidth = $('#pagination').width();
	//$('#pagination').css('margin-left',(0-paginationwidth));

	pagination.eq(0).addClass('current');

	function ADDLI(){
		for(var i = 0; i <= numpic; i++){
			ulcontent += '<li>' + '<a href="#">' + (i+1) + '</a>' + '</li>';
		}

		$('#slidelist').after(ulstart + ulcontent + ulend);
	}

	pagination.on('click',DOTCHANGE);

	function DOTCHANGE(){

		var changenow = $(this).index();

		$('#slidelist li').eq(nownow).css('z-index','39');
		$('#slidelist li').eq(changenow).css({'z-index':'38'}).show();
		pagination.eq(changenow).addClass('current').siblings('li').removeClass('current');
		$('#slidelist li').eq(nownow).fadeOut(400,function(){$('#slidelist li').eq(changenow).fadeIn(500);});
		nownow = changenow;
	}

	pagination.mouseenter(function(){
		inout = 1;
	});

	pagination.mouseleave(function(){
		inout = 0;
	});

	function GOGO(){
		var NN = nownow+1;
		if( inout == 1 ){
			} else {
			if(nownow < numpic){
			$('#slidelist li').eq(nownow).css('z-index','39');
			$('#slidelist li').eq(NN).css({'z-index':'38'}).show();
			pagination.eq(NN).addClass('current').siblings('li').removeClass('current');
			$('#slidelist li').eq(nownow).fadeOut(400,function(){$('#slidelist li').eq(NN).fadeIn(500);});
			nownow += 1;

		}else{
			NN = 0;
			$('#slidelist li').eq(nownow).css('z-index','39');
			$('#slidelist li').eq(NN).stop(true,true).css({'z-index':'38'}).show();
			$('#slidelist li').eq(nownow).fadeOut(400,function(){$('#slidelist li').eq(0).fadeIn(500);});
			pagination.eq(NN).addClass('current').siblings('li').removeClass('current');

			nownow=0;

			}
		}
		TT = setTimeout(GOGO, SPEED);
	}

	TT = setTimeout(GOGO, SPEED);
});

