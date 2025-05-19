import 'package:flutter/material.dart';
import 'package:android_app/models/hub.dart';
import 'package:android_app/models/node.dart';
import 'package:android_app/services/api_service.dart';
import 'sensor_list_page.dart';

class NodeListPage extends StatefulWidget {
  final Hub hub;
  const NodeListPage({required this.hub, Key? key}):super(key:key);
  @override _NodeListPageState createState()=>_NodeListPageState();
}

class _NodeListPageState extends State<NodeListPage> {
  List<Node> _nodes = [];
  bool _loading = true;

  @override void initState(){super.initState();_load();}
  Future<void> _load()async{
    try {final data=await ApiService.fetchNodes(widget.hub.id);
    setState((){
      _nodes=data;
      _loading=false;
    });}
    catch(_){setState(()=>_loading=false);}
  }
  Future<void> _showForm({Node? node})async{
    final loc=TextEditingController(text:node?.location);
    final key=GlobalKey<FormState>();
    final edit=node!=null;
    await showDialog(context:context,builder:(_)=>AlertDialog(
        title:Text(edit?'Edit Node':'Add Node'),
        content:Form(key:key,child:TextFormField(
          controller:loc,
          decoration:InputDecoration(labelText:'Location'),
          validator:(v)=>v==null||v.isEmpty?'Required':null,
        )),
        actions:[
          TextButton(onPressed:()=>Navigator.pop(context),child:Text('Cancel')),
          TextButton(onPressed:()async{
            if(!key.currentState!.validate())return;
            try{
              if(edit) await ApiService.updateNode(node!.id, loc.text);
              else     await ApiService.createNode(widget.hub.id, loc.text);
              Navigator.pop(context);
              _load();
            }catch(_){ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text('Save failed')));}
          },child:Text('Save'))
        ]
    ));
  }
  Future<void> _confirmDelete(Node node)async{
    if(await showDialog<bool>(context:context,builder:(_)=>AlertDialog(
        title:Text('Delete Node?'),content:Text('Remove \"${node.location}\"?'),
        actions:[TextButton(onPressed:()=>Navigator.pop(context,false),child:Text('Cancel')),
          TextButton(onPressed:()=>Navigator.pop(context,true),child:Text('Delete'))]
    ))==true){
      try{await ApiService.deleteNode(node.id);_load();}catch(_){ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text('Delete failed')));}    }
  }
  @override Widget build(BuildContext context){
    if(_loading) return Center(child:CircularProgressIndicator());
    return Scaffold(
      appBar:AppBar(title:Text('Nodes - ${widget.hub.name}')),
      body:ListView.builder(itemCount:_nodes.length,itemBuilder:(ctx,i){final n=_nodes[i]; return ListTile(
        title:Text(n.location),
        trailing:Row(mainAxisSize:MainAxisSize.min,children:[
          IconButton(icon:Icon(Icons.edit),onPressed:()=>_showForm(node:n)),
          IconButton(icon:Icon(Icons.delete),onPressed:()=>_confirmDelete(n)),
        ]),
        onTap:()=>Navigator.push(context,MaterialPageRoute(builder:(_)=>SensorListPage(node:n))),
      );}),
      floatingActionButton:FloatingActionButton(child:Icon(Icons.add),onPressed:()=>_showForm()),
    );
  }
}
