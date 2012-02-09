   function show_form(name,display_name,mode,id,width){   	
   	$('#'+name+'_form'+" input[type=submit]").val("Сохранить");
   	if (mode == 'edit'){
	   	$.getJSON('/ajax/'+name+'/'+id, function(data) {
	   	for (field in data[0].fields){
	  		$('#id_'+field).val(data[0].fields[field]);	  
	  	}
	  	$('#'+name+"_id").val(id);  	
	  	action="Изменить"
	  	$('#'+name+'_form').attr('action','/edit_'+name+'/');
	  	$('#'+name+'_form').dialog({modal: true, width: width, 
   		resizable: false,title: action+' '+display_name});  	
		});
		
	}else if( mode='add'){
		action="Добавить"
		$('#'+name+'_form').attr('action','/add_'+name+'/');
		$('#'+name+'_form').dialog({modal: true, width: width, 
   		resizable: false,title: action+' '+display_name});
	}
  } 
  
  function show_form_(event,name,display_name,mode,width){  
   	id=event.target.id.split('_')[1];
   	$('#'+name+'_form'+" input").val('');
   	show_form(name,display_name,mode,id,width);
   	event.preventDefault();
  }
  
  function show_form__(event,name,display_name,mode,width,before_show){  	  
   	id=event.target.id.split('_')[1];
   	$('#'+name+'_form'+" input").val('');
   	before_show(name+'_form');   	
   	show_form(name,display_name,mode,id,width);
   	
   	event.preventDefault();
  }