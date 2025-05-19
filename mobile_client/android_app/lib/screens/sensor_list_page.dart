import 'package:flutter/material.dart';
import 'package:android_app/models/node.dart';
import 'package:android_app/models/sensor.dart';
import 'package:android_app/services/api_service.dart';

class SensorListPage extends StatefulWidget {
  final Node node;
  const SensorListPage({required this.node, Key? key}):super(key:key);
  @override _SensorListPageState createState()=>_SensorListPageState();
}

class _SensorListPageState extends State<SensorListPage> {
  List<Sensor> _sensors = [];
  bool _loading = true;

  @override void initState(){super.initState();_load();}
  Future<void> _load() async{
    try{ final ss = await ApiService.fetchSensors(widget.node.id);
    setState((){_sensors=ss;
          _loading=false;}); }
    catch(_){setState(()=>_loading=false);}
  }
  Future<void> _showForm({Sensor? sensor}) async{
    final typeCtrl = TextEditingController(text:sensor?.type);
    final pinCtrl  = TextEditingController(text:sensor?.pin);
    final key = GlobalKey<FormState>();
    final edit = sensor!=null;
    await showDialog(context:context,builder:(_)=>AlertDialog(
        title: Text(edit?'Edit Sensor':'Add Sensor'),
        content:Form(key:key,child:Column(mainAxisSize:MainAxisSize.min,children:[
          TextFormField(controller:typeCtrl,decoration:InputDecoration(labelText:'Type'),validator:(v)=>v==null||v.isEmpty?'Required':null),
          TextFormField(controller:pinCtrl, decoration:InputDecoration(labelText:'Pin'), validator:(v)=>v==null||v.isEmpty?'Required':null),
        ])),
        actions:[TextButton(onPressed:()=>Navigator.pop(context),child:Text('Cancel')),
          TextButton(onPressed:() async{
            if(!key.currentState!.validate()) return;
            try {
              if(edit) await ApiService.updateSensor(sensor!.id, typeCtrl.text, pinCtrl.text, sensor!.alertEnabled);
              else     await ApiService.createSensor(widget.node.id, typeCtrl.text, pinCtrl.text);
              Navigator.pop(context);
              _load();
            } catch(_) { ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text('Save failed')));}
          }, child:Text('Save'))]
    ));
  }
  Future<void> _confirmDelete(Sensor sensor) async {
    if(await showDialog<bool>(context:context,builder:(_)=>AlertDialog(
        title:Text('Delete Sensor?'),content:Text('Remove \"${sensor.type}\"?'),
        actions:[TextButton(onPressed:()=>Navigator.pop(context,false),child:Text('Cancel')),
          TextButton(onPressed:()=>Navigator.pop(context,true),child:Text('Delete'))]
    ))==true) {
      try { await ApiService.deleteSensor(sensor.id); _load(); } catch(_) { ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text('Delete failed'))); }
    }
  }
  @override
  Widget build(BuildContext context) {
    if (_loading) return Center(child: CircularProgressIndicator());
    return Scaffold(
      appBar: AppBar(title: Text('Sensors - ${widget.node.location}')),
      body: ListView.builder(
        itemCount: _sensors.length,
        itemBuilder: (ctx, i) {
          final s = _sensors[i];
          return ListTile(
            title: Text(s.type),
            subtitle: Text('Pin: ${s.pin}'),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Alert-enable switch
                Switch(
                  value: s.alertEnabled,
                  onChanged: (val) async {
                    try {
                      final updated = await ApiService.updateSensor(
                        s.id,
                        s.type,
                        s.pin,
                        val,
                      );
                      setState(() {
                        s.alertEnabled = updated.alertEnabled;
                      });
                    } catch (_) {
                      ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Failed to update alert setting'))
                      );
                    }
                  },
                ),
                // Edit / Delete as before
                IconButton(
                  icon: Icon(Icons.edit),
                  onPressed: () => _showForm(sensor: s),
                ),
                IconButton(
                  icon: Icon(Icons.delete),
                  onPressed: () => _confirmDelete(s),
                ),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.add),
        onPressed: () => _showForm(),
      ),
    );
  }
}