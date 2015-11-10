(function(){
    "use strict";
    var App;

    App = {
        init: function() {
            App.setCopyRight();
            if (window.innerHeight >= 650 && window.innerWidth >= 700) {
                $("#banner1").css("height", window.innerHeight-90)
                $('#header').affix({offset: window.innerHeight})
                $("#mainButton").css("width", "60%");
                $("#mainButton").css("text-align", "left");
                $("#mainButton").css("font-size", 50);
                $("#buttonHolder").css("padding-top", 30);
                $("#mainButtonIcon").css("font-size", 40);
                $("#mainButton2").css("width", "60%");
                $("#mainButton2").css("font-size", 50); 
                $("#mainButtonIcon2").css("font-size", 40);
            } else {
                $("#banner1").css("height", window.innerHeight-90);
                $("#ha").css("font-size", 40);
                $("#ha2").css("font-size", 24);
                // $("#q1").css("width", "100%");
                // $("#faq").css("padding-top", 500);

                // $("#qp").text("Get started");
                
                // $("#qp2").text("Get started");
            }
            
            $('#header').affix({
              offset: window.innerHeight
            })
        },
        setCopyRight: function() {
            var date, year;
            date = new Date();
            year = date.getFullYear();
            // $("#copyright").text(year);
        },
        setFixedNavbar: function() {
            var $win, $header;
            var h = 280;
            $win = $(window);
            $header = $('#header')
            $win.on('scroll', function() {
                if ($win.scrollTop() > h) {
                    $header.addClass('navbar-fixed-top');
                } else {
                    $header.removeClass('navbar-fixed-top');
                }
            })
        }
    }

    App.init();

}).call(this);