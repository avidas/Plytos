$(document).ready(function () {

    function updateTodo(val, elem){

        var className;
        var sections = [];

        //For each tag
        elem.each(function() {

            //console.log(className);
            //console.log(elem);
            // update counter for to do item
            var newVal = 0;
            
            if (parseInt($( elem ).text() ) ) {
                newVal = parseInt($( elem ).text()) + val;
            } else if (val >= 0) {
                newVal = val;
            }
            // split string of all classes into array
            className = $( this ).attr('class').split(/\s+/);
            //update sections
            sections.push({"section_name": className[0], "value": newVal});

            /*        
            var sectionItem = 'li#' + className[0] + ' p span h3';
            var todoElem = '<span class="todo_count badge badge-warning pull-right fa fa-paperclip">&nbsp <span class="count"></span></span>';
            var todoCounter = $('> span.todo_count span.count', sectionItem).length ? $('> span.todo_count span.count', sectionItem) : $(todoElem).appendTo(sectionItem);
            //var elem = 'li#' + className[0] + " span.todo_count span.count";
            todoCounter.text( newVal );
            */

            // first class name is same as id of reseume section
            // find the count item on section
            var elem = 'li#' + className[0] + " span.todo_count span.count";
            if( $( elem ).length ) {
                $( elem ).text( newVal );
            } else {
                var x = 0;

            }
        });

        var pathArray = window.location.pathname.split( '/' );

        data = {
            "slug" : pathArray[2],
            "sections" : sections
        }

        $.ajax({
            type : "POST",
            url: "/resumes/todos",
            data: JSON.stringify(data, null, '\t'),
            contentType: 'application/json;charset=UTF-8',
            success: function(result) {
                console.log(result);
            }
        });

        return val > 0 ? "UNDO" : "TODO";
    }

    $('.todo').click(function () {
        $( this ).text(function(i, text){
            //select the tags corresponding to the clicked comment
            var $comm = $( this ).parent().parent().parent().children('p').children('span.category');
            return text === "TODO" ? updateTodo(1, $comm) : updateTodo(-1, $comm);
        })   
    });
});
