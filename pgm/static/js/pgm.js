var table;

$(document).ready(function(){
   $('.button-left').click(function(){
       $('.sidebar').toggleClass('fliph');
   });

/*    $('.js-datepicker').datepicker({
    	format: 'dd/mm/yyyy',
    	language: 'pt-BR',
    });
*/
    $(".moneymask").maskMoney({allowNegative: false, thousands:'.', decimal:',', affixesStay: false});

    table = $('.datatables').DataTable({
        order: [[1,'asc'],[ 0, 'asc' ],[ 2, 'asc' ]],
        lengthMenu: [[5, 10, 15, -1], [5, 10, 15, "All"]],
        stateSave: true,
        language: {
                "url": "//cdn.datatables.net/plug-ins/1.10.19/i18n/Portuguese-Brasil.json"
        },
		footerCallback: function ( row, data, start, end, display ) {
		    var api = this.api(), data;

		    // Remove the formatting to get integer data for summation
		    var intVal = function ( i ) {
		        return typeof i === 'string' ?
		            i.replace(/[\.,]/g, '')*1 :
		            typeof i === 'number' ?
		                i : 0;
		    };

		    // Total over all pages
		    total = api
		        .column( 4, {filter: 'applied'} )
		        .data()
		        .reduce( function (a, b) {
		            return intVal(a) + intVal(b);
		        }, 0 );

		    // Total over this page
		    pageTotal = api
		        .column( 4, { page: 'current'} )
		        .data()
		        .reduce( function (a, b) {
		            return intVal(a) + intVal(b);
		        }, 0 );

		    // Update footer
		    $( api.column( 4 ).footer() ).html(
		        'Total da página: '+(pageTotal/100).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) +' ( Total: '+ (total/100).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) +' )'
		    );
		},
        stateLoaded: function (settings, data) {
            console.log( 'Saved filter was: '+data );
        },
        initComplete: function () {
                
                this.api().column(3).every( function () {
                    var column = this;


                    var select = $('<select class="form-control-sm" id="search_year"><option value=""></option></select>')
                        .appendTo( $("#column_search_year").empty() ).on('change', function () {
                            var selection = parseInt(this.value);

                            if(column.search() !== this.value && isNaN(selection) == false){

                                var first = this.value.substring(0,3);
                                var second = this.value.substring(1,2)+"-9";
                                var third = this.value.substring(2,3)+"-9";
                                var four = this.value.substring(3,4);

                                var myregexp = '^'+first+'['+four+']|2['+second+']['+third+']['+four+']$';

                                if(four == '9'){
                                    four = '0-9';
                                    third = parseInt(third)+1;
                                    third = third+'-9';
                                    myregexp = '^'+first+'[9]|2['+second+']['+third+']['+four+']$';
                                }else{
                                    four = four+'-9';
                                    myregexp = '^'+first+'['+four+']|2['+second+']['+third+']['+four+']$';
                                }


                                if(first == '199'){
                                    if(this.value.substring(3,4) == '9'){
                                        four = '9';
                                    }else{
                                        four = this.value.substring(3,4) + '-9';
                                    }
                                    myregexp = '^'+first+'['+four+']|2[0-9]{3}$';
                                }

                                column.search( myregexp , true, false, true ).draw();
                            }else{
                                column.search('').draw();
                            }

                        });

                    column.data().unique().sort().each( function ( d, j ) {
                        select.append( '<option value="'+d+'">'+d+'</option>' )
                    } );



                }),

                this.api().column(2).every( function () {
                    var column = this;

                    var myregexp;

                        $('input:radio[name="radio_doc"]').change(function () {
                            var checkedvalue = parseInt(this.value);
                            if(checkedvalue == 0){
                                column.search('').draw();
                            }else if(checkedvalue == 1){
                                myregexp = '^\\d{3}\\.\\d{3}\\.\\d{3}\\-\\d{2}$';
                                column.search(myregexp, true, false, true).draw();
                            }else{
                                myregexp = '^\\d{2}\\.\\d{3}\\.\\d{3}\\/\\d{4}\\-\\d{2}$';
                                column.search(myregexp, true, false, true).draw();
                            }
                        });
                })


        }
    }); // end of datatables api


 /*   function filteryear(min) {

        $.fn.dataTable.ext.search.push(

            function( settings, data, dataIndex ) {

                var year = parseInt( data[3] ) || 0;
                var selection = parseInt( min, 10 )

                if ( ( isNaN(selection) ) ||
                     ( selection <= year ) )
                {
                    return true;
                }
                return false;
            }
        );

        table.draw();

    };


    $('input:radio[name="radio_doc"]').change(function () {

        $.fn.dataTable.ext.search.push(

            function( settings, data, dataIndex ) {

                var doc = data[2];
                radioval = parseInt($('input:radio[name="radio_doc"]:checked').val());
                var doclen = (doc.length === 14 ? 1 : 2)
                if (doclen == radioval){
                    return true;
                }else if(radioval == 0){
                    return true;
                }
                return false;
            }
        );

        table.draw();
    });

*/
    $('.js-datepicker').mask('00/00/0000');

    $("#id_cpf_cnpj").mask('000.000.000-00', {reverse: true});

    $("input[type=radio]").on("click", function () {

       if($(this).val() == '1'){
           $("#id_cpf_cnpj").unmask();
           $("#id_cpf_cnpj").mask('000.000.000-00', {reverse: true});
       }else if($(this).val() == '2'){
           $("#id_cpf_cnpj").unmask();
           $("#id_cpf_cnpj").mask('00.000.000/0000-00', {reverse: true});
       }
    });


    $('form').submit(function(e){
        preloadActive();
    });

    $('.mySpinner').click(function(e){
        preloadActive();
    });

    $("#_enviaremessacdl").click(function () {

        preloadActive();

        var cdas = [];

        var url = $('#_formremessacdl').prop('action');

        $("input", table.rows({search:'applied'}).nodes()).each(function () {
            cdas.push($(this).val());
            table.rows($(this).parents('tr')).remove();
        });


        $.get(url, {'_cdas': cdas},function(response){
               preloadDeActive();
               bootbox.alert(response.message, function () {
                   table.draw();
               });
        });

    });

});

function addCheckbox(container, name) {

   $('<input />', { type: 'checkbox', id:name, name: name, value: name, checked:true }).appendTo(container);
   $('<label />', { 'for': 'cb'+name, text: name }).appendTo(container);
}

function preloadActive(){

    $("#modalajaxloader").modal({
	      backdrop: 'static', // Modal can be dismissed by clicking outside of the modal
	      //opacity: .2, // Opacity of modal background
          keyboard: false
    });

	$("#modalajaxloader").modal('show');

};

function preloadDeActive(){

	$("#modalajaxloader").modal('hide');
};
