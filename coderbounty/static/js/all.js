//ajax loader hide here
$("#loading").ajaxStop(function(){
  $(this).hide();
});
//ajax loader show here
$("#loading").ajaxStart(function(){
  $(this).show();
});

$('.time').selectbox({
    'onChangeCallback':function(event){
        event.container.closest('.search_area').hide();

        $('.content_area_right').ajaxStop(function(){
          $('.content_area_right').removeClass('ajax_loading')
        });

        var parent = this.onChangeParams.container.parents('.content_area');
        $(parent).children('.content_area_right').addClass('ajax_loading');
        //$('#mf141').css({float:'none'}).addClass('ajax_loading');

        var dataString = 'url='+ encodeURIComponent(event.container.closest('.content_area_left').next().find('a').attr('href')) + '&bounty=' + event.container.closest('.content_area_left').find('.add2cart').val() + '&limit=' + event.selectedVal;
        add_issue_ajax(dataString);
    }    
});



$(document).ready(function() {

    var login_link = $('#login_link').live("mouseover", function(){
        $('#tooltip_wrapper').show();
        $('.tooltip').slideDown('fast', function(){
            $("input#username").focus();
        });

        return false;
    });

    login_link.live("click", function(){
        if($('.tooltip').not(':visible')){
            $('#tooltip_wrapper').show();
            $('.tooltip').slideDown('fast', function(){
                $("input#username").focus();
            });
        }
        return false;
    });



    $('html').click(function() {
        if($('.tooltip').is(':visible')){
            $('.tooltip').slideUp('fast',function(){
                $('#tooltip_wrapper').hide();
            });
        }
        
    });

    $('#login_link').click(function(event){
        $("input#username").focus();
        event.stopPropagation();
        return false;
    });
    

    $('.tooltip').click(function(event){
        event.stopPropagation();
    });

    if($('#message').val() || $('#message').children().length){

        if($('#message').find('span').html() == "Please login"){
            $('#tooltip_wrapper').show();
            $('.tooltip').slideDown('fast', function(){
                $("input#username").focus();
            });
        }
        $('#message').fadeIn().delay('3000').fadeOut();
    }
    if($('#q').val()){
        $.each($('#q').val().replace(/['"]/g,'').split(" "), function(idx, val) {
            $("#issues").highlight(val);
        });
    }
    $('div.left_top a').hover(
        function(event){
            $(this).closest('.content_area_left').find('.bounties').show();
        },
        function(event){
            $(this).closest('.content_area_left').find('.bounties').hide();
        });


    (function() {
        var uv = document.createElement('script');
        uv.type = 'text/javascript';
        uv.async = true;
        uv.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'widget.uservoice.com/idrfbcpaAG0SSGR3MU7hIA.js?media="screen"';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(uv, s);
    })();
    /* disabled until we send stuff to twitter
    var tweets = new Array();
    var refreshId = setInterval(function(){
        $.ajax({
            url: 'http://api.twitter.com/1/statuses/user_timeline.json/',
            type: 'GET',
            dataType: 'jsonp',
            data: {
                screen_name: 'coderbounty',
                include_rts: true,
                count: 1,
                include_entities: true
            },
            success: function(data) {

                for (var i = 0; i < data.length; i++) {
                    if(jQuery.inArray(data[i].id, tweets)=="-1"){
                        $('.center_box').html(data[i].text);
                        $('.center_box').slideDown().delay('10000').slideUp();
                        tweets.push(data[i].id);
                    }
                }
            }
        });
    },80000);
    */
    $('.profile_box a').click(function(event){
        
        var current_a=$(this);
        var verification_code_input=$(this).next().next()
        if($(this).next().val()==""){
            $('.message_area').html("please enter a value");
            $(this).next().focus();
            return false;
        }
        $(this).next().next().slideDown(function(){
            if($(this).val()==""){
                $(this).val("Verfication Code");
            }
            $(this).click(function(){
                if($(this).val()=="Verfication Code"){
                    $(this).val("");
                }
            });
            $(this).blur(function(){
                if($(this).val()==""){
                    $(this).val("Verfication Code");
                }
            });
        });

        if(verification_code_input.val()!="Verfication Code"){
            verification_code = verification_code_input.val();
        }
        $.get('/verify/'+$(this).attr('id')+"/", {
            username: $(this).next('input').val(),
            verification_code: verification_code
        }, function(data) {
            if(data=="Thanks for verifying your account. Happy coding!"){
                verification_code_input.slideUp(function(){
                    current_a.replaceWith("<span class='verified'>verified &#10003;</span>");
                });
            }
            $('.message_area').html(data);
        });
        return false;
    });
    
});


$('.tweet').click(function(event) {
    var width  = 575,
    height = 400,
    left   = ($(window).width()  - width)  / 2,
    top    = ($(window).height() - height) / 2,
    url    = this.href,
    opts   = 'status=1' +
    ',width='  + width  +
    ',height=' + height +
    ',top='    + top    +
    ',left='   + left;

    var tweet_window = window.open(url, 'twitter', opts);
    //tweet_window.closed/
    return false;
});

//url / search
function blank(a) {
    if(a.value == a.defaultValue) a.value = "";
}
function unblank(a) {
    if(a.value == "") a.value = a.defaultValue;
}


///analytics
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-11010957-2']);
_gaq.push(['_trackPageview']);

(function() {
    var ga = document.createElement('script');
    ga.type = 'text/javascript';
    ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(ga, s);
})();


//facebook
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/all.js#xfbml=1";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


//facebook analytics
window.fbAsyncInit = function() {
    FB.Event.subscribe('edge.create', function(targetUrl) {
        _gaq.push(['_trackSocial', 'facebook', 'like', targetUrl]);
    });
}


//twitter analytics
function followCallback(intent_event) {
    if (intent_event) {
        _gaq.push(['_trackSocial', 'twitter', 'follow']);
    }
}


$(function() {

    $("#add_issue").click(function() {
        $(this).ajaxStop(function(){
          $(this).removeClass('ajax_loading');
        });

        $('#message').hide().html("");

        var url = $("input#url").val();
        if ((url == "") || (url == "Enter a link to a Github, Google Code or Bitbucket issue")) {
            $('#message').html("Please enter a link to a Github or Google Code issue");
            $("input#url").focus();
            $('#message').fadeIn().delay('3000').fadeOut();
            return false;
        }

        var bounty = $("select#bounty").val()
        if (bounty == "") {
            $('#message').html("Please enter a bounty");
            $("select#bounty").focus();
            $('#message').fadeIn().delay('3000').fadeOut();
            return false;
        }

        var limit = $("select#limit").val()
        if (limit == "") {
            $('#message').html("Please enter a time limit");
            $("select#limit").focus();
            $('#message').fadeIn().delay('3000').fadeOut();
            return false;
        }
        var dataString = 'url='+ encodeURIComponent(url) + '&bounty=' + bounty + '&limit=' + limit;
        $(this).addClass('ajax_loading');
        add_issue_ajax(dataString);
        return false;
    });
});

function add_issue_ajax(dataString){
            
    $.ajax({
        type: "GET",
        url: "/add/",
        data: dataString,
        success: function(data) {
            var obj = jQuery.parseJSON(data);
            if(obj.balance && obj.balance != "None"){
                if (obj.balance < $('#balance').html().replace("\$","")){
                    $('#balance').fadeOut('',function(){
                        $('#balance').html('$'+obj.balance)
                    });
                    $('#balance').fadeIn();
                }
            }
            $('#message').html(obj.message);
            $('#message').fadeIn().delay('3000').fadeOut();

            if(obj.message == "Please Login"){
                $('#tooltip_wrapper').show();
                $('.tooltip').slideDown('fast', function(){
                    $("input#username").focus();
                });
                return false;
            }
            if(obj.checkout_uri){
                WePay.iframe_checkout("checkout_div_id", obj.checkout_uri);
                popup("#dialog-box");
            //handle case where user has no balance and we want to display the issue in the bg
            }else{
                var $new_issue = $('<div class="new_issue"/>');
                $('#first_issue').after($new_issue);
                $new_issue.load('/load_issue/', {
                    'issue':obj.issue,
                    csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value
                }, function(event){
                    
                    $new_issue.find('.add2cart').selectbox({
                        'onChangeCallback':function(event){
                            event.container.closest('.content_area_left').find('.search_area').show()
                        }
                    });
                    
                    
                    $new_issue.find('.time').selectbox({
                        'onChangeCallback':function(event){
                            event.container.closest('.search_area').hide();
                            var dataString = 'url='+ encodeURIComponent(event.container.closest('.content_area_left').next().find('a').attr('href')) + '&bounty=' + event.container.closest('.content_area_left').find('.add2cart').val() + '&limit=' + event.selectedVal;
                            add_issue_ajax(dataString);
                        }    
                    });
                    $new_issue.find('div.left_top a').hover(
                        function(event){
                            $(this).closest('.content_area_left').find('.bounties').show();
                        },
                        function(event){
                            $(this).closest('.content_area_left').find('.bounties').hide();
                        });
                    $new_issue.find('.left_bottom a').hover(function(event){
                        $(this).closest('.content_area_left').find('.watch').toggle();
                    });
                    $new_issue.find('.selectbox').click(function(event){
                        event.stopPropagation();
                    });
                    id = $new_issue.find('.left_bottom a').attr("id");

                });
                $new_issue.slideDown('slow');
            }
        }
    });
}

//login
$('#loginForm').submit(function() {

    var username = $("input#username").val();
    var password = $("input#password").val();

    var csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    $.post('/login/', {
        username: username,
        password: password,
        csrfmiddlewaretoken: csrfmiddlewaretoken
    }, function(data) {

        if(data!=''){
            $(".tooltip").slideUp();

            $('#user_header').fadeOut(function(){
                $('#user_header').html(data);
            });

            $('#user_header').fadeIn();
            $('#message').hide();
            $('#message').html("<span class='success'>Welcome back " + username + "!</span>");
            $('#message').fadeIn().delay('3000').fadeOut();
            $("input#username").val('');
            $("input#password").val('');
            $('#profile-box').load('/profile/', function(){
                $('#profileForm').submit(function() {
                    return do_profile();
                });
                $('a.btn-ok, a.button ').click(function () {
                    $('#dialog-overlay, #profile-box').hide();
                    return false;
                });
            });
        }else{
            $('#login_message').hide();
            $('#login_message').html("Please try again");
            $('#login_message').fadeIn().delay('3000').fadeOut();
        }

    });
    return false;
});



$('#profileForm').submit(function() {
    $('#save_profile').attr('src', '/static/images/loading.gif');
    $(this).ajaxStop(function(){
      $('#save_profile').attr('src', '/static/images/save.jpg');
    });
    return do_profile();
});


//join
$('#joinForm').submit(function() {

    $.post('/join/', {
        email: $("input#id_email").val(),
        password1: $("input#id_password1").val(),
        password2: $("input#id_password2").val(),
        username: $("input#id_username").val(),
        user_name: $("input#id_user_name").val(),
        agree: $("[name='agree']").attr('checked'),
        magic: $("input#id_magic").val(),
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value

    }, function(data) {

        if(data!=''){
            $(".join_tooltip").slideUp();
            $('#user_header').fadeOut(function(){
                $('#user_header').html(data);
            });
            $('#user_header').fadeIn();
            $('#message').hide();
            $('#message').html("<span class='success'>Thanks for joining Coder Bounty.  Add some issues!</span>");
            $('#message').fadeIn().delay('3000').fadeOut();
            $("input#id_username").val('');
            $("input#id_email").val('');
            $("input#id_password1").val('');
            $("input#id_password2").val('');
            $('#join_message').html('');
            $('#dialog-overlay, #join-box').hide();
            $('#profile-box').load('/profile/', function(){
                $('#profileForm').submit(function() {
                    return do_profile();
                });
                $('a.btn-ok, a.button ').click(function () {
                    $('#dialog-overlay, #profile-box').hide();
                    return false;
                });
            });
        }else{
            var message = "Please try again";
            if(!$("input#id_username").val()){
                message = "Please enter a username";
            }
            if(!$("input#id_email").val()){
                message = "Please enter an email address";
            }
            if(!$("input#id_password1").val()){
                message = "Please enter a password";
            }
            if(!$("input#id_password2").val()){
                message = "Please re-enter your password";
            }
            if(!$("[name='agree']").attr('checked')){
                message = "You must agree to the terms";
            }
            $('#join_message').hide();
            $('#join_message').html(message);
            $('#join_message').fadeIn().delay('3000').fadeOut();
        }
    });
    return false;
});


$('#logout_link').live("click", function(){
    $.get('/logout/', {
        }, function(data) {
            if (data!=''){
                $('#user_header').fadeOut(function(){
                    $('#user_header').html(data);
                });
                $('#user_header').fadeIn();
                $('#message').hide();
                $('#message').html("<span class='success'>Logged out successfully.</span>");
                $('#message').fadeIn().delay('3000').fadeOut()
            }
        });
    return false;
});

$('.left_bottom a').hover(function(event){
    $(this).closest('.content_area_left').find('.watch').toggle();
});

$('.left_bottom a').click(function(event){
    var bounty_change = $(this).closest('.content_area_left').find('.bounty_change');
    var status_change = $(this).closest('.content_area_left').find('.status_change');
    var eye_image_number=''
    if(bounty_change.attr('checked') == "checked" && status_change.attr('checked') == "checked"){
        status_change.removeAttr("checked");
        eye_image_number=3;
    }else if(bounty_change.attr('checked') == "checked" && !status_change.attr('checked')){
        bounty_change.removeAttr("checked");
        status_change.attr('checked', true);
        eye_image_number=3;
    }else if(!bounty_change.attr('checked') && status_change.attr('checked') == "checked"){
        bounty_change.removeAttr("checked");
        status_change.removeAttr("checked");
        eye_image_number=2;
    }else if (!bounty_change.attr('checked') && !status_change.attr('checked')){
        bounty_change.attr('checked', true);
        status_change.attr('checked', true);
    }
    id = $(this).attr("id");
    watch_count_span = $(this).find('strong');


    $.get('/watch/', {
        issue: id,
        bounty: bounty_change.attr('checked'),
        status: status_change.attr('checked')
    }, function(data) {
     

        var obj = jQuery.parseJSON(data);

        if(obj.message=="Please Login"){
            $('#tooltip_wrapper').show();
            $('.tooltip').slideDown('fast', function(){
                $("input#username").focus();
                $('#message').html(obj.message);
                $('#message').fadeIn().delay('3000').fadeOut();
            });
        }else{
            watch_count_span.fadeOut('',function(){
                watch_count_span.html(data!=0?data:"&nbsp;");
                watch_count_span.css('background-image', 'url(/static/images/eye_img'+eye_image_number+'.jpg)');
            });
            watch_count_span.fadeIn();
        }
    });
    return false;
});


$('#search_form').submit(function(){
    return do_search();
});
$('#order').change(function(){
    return do_search();
});
$('#search').click(function(){
    return do_search();
});

$('.menu ul li a').click(function(event){
    if($(this).hasClass('join')){
        popup("#join-box");
        return false;
    }else{
        $('input#status').val($(this).html().toLowerCase());
        $(this).parent().addClass('active');
        $('.menu ul li a').not($(this)).parent().removeClass('active');
        return do_search();
    }
});

function do_profile(){
    $.post('/profile/', {
        username: $("input#profile_username").val(),
        email: $("input#profile_email").val(),
        password: $("input#profile_password").val(),
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
        payment_wepay: $("input#payment_wepay").attr('checked'),
        payment_paypal: $("input#payment_paypal").attr('checked'),
        payment_service_email: $("input#payment_service_email").val()

    }, function(data) {
        $("input#profile_password").val('');
        $('.message_area').hide();
        $('.message_area').html(data);
        $('.message_area').fadeIn().delay('3000').fadeOut();

    });
    return false;
}


function do_search(){

    var q = $('input#q').val();
    var order = $('select#order').val();
    var status = $('input#status').val();
    if (q == "Search"){
        q="";
    }
        
    var csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    $('#issues').load("/?q="+encodeURIComponent(q)+"&csrfmiddlewaretoken="+csrfmiddlewaretoken+"&order="+encodeURIComponent(order)+"&status="+encodeURIComponent(status),
        function(data){
            if (/^\s+$/.test(data) && q!="Search"){
                $('.center_box').html("Your search did not match any issues")
                $('.center_box').slideDown().delay('3000').slideUp();;
            }
            if (q){
                $.each(q.replace(/['"]/g,'').split(" "), function(idx, val) {
                    $("#issues").highlight(val);
                });
            }
             
            $('.add2cart').selectbox({
                'onChangeCallback':function(event){
                    event.container.closest('.content_area_left').find('.search_area').show()
                }
            });
                    
            $('.time').selectbox({
                'onChangeCallback':function(event){
                    event.container.closest('.search_area').hide();
                    var dataString = 'url='+ encodeURIComponent(event.container.closest('.content_area_left').next().find('a').attr('href')) + '&bounty=' + event.container.closest('.content_area_left').find('.add2cart').val() + '&limit=' + event.selectedVal;
                    add_issue_ajax(dataString);
                }    
            });
            $('div.left_top a').hover(
                function(event){
                    $(this).closest('.content_area_left').find('.bounties').show();
                },
                function(event){
                    $(this).closest('.content_area_left').find('.bounties').hide();
                });
            $('.left_bottom a').hover(function(event){
                $(this).closest('.content_area_left').find('.watch').toggle();
            });
            $('.selectbox').click(function(event){
                event.stopPropagation();
            });
        });
    return false;
}



$("input#url").bind("dragenter dragover", function(){
    $("input#url").val('');
});



$(document).keyup(function(e) {
           
    if (e.keyCode == 27) { 
        $('#dialog-overlay, #dialog-box, #about-box, #shirt-box, #help-box, #profile-box, #terms-box, #join-box').hide();		
		
    }   
    return false;
});

function popup(name){
    if (name==undefined){
        name="#dialog-box";
    }
    
    var maskHeight = $(document).height();  
    var maskWidth = $(window).width();
	
    var dialogTop =  (maskHeight/3) - ($(name).height());  
    var dialogLeft = (maskWidth/2) - ($(name).width()/2); 
	
    $('#dialog-overlay').css({
        height:maskHeight, 
        width:maskWidth
    }).show();
    $(name).css({
        top:dialogTop, 
        left:dialogLeft
    }).show();
    
    $('a.btn-ok, a.button ').click(function () {		
        $('#dialog-overlay, '+name).hide();
        return false;
    });

    $('a.button-terms ').click(function () {		
        $('#terms-box').hide();
        return false;
    });
    
    $(window).resize(function () {
        if (!$(name).is(':hidden')) {
           
       	
            var maskHeight = $(document).height();  
            var maskWidth = $(window).width();
	
            var dialogTop =  (maskHeight/3) - ($(name).height());  
            var dialogLeft = (maskWidth/2) - ($(name).width()/2); 
            $('#dialog-overlay').css({
                height:maskHeight, 
                width:maskWidth
            }).show();
            $(name).css({
                top:dialogTop, 
                left:dialogLeft
            }).show();
        }
    });	
			
}




