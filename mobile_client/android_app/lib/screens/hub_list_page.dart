import 'package:flutter/material.dart';
import 'package:android_app/models/hub.dart';
import 'package:android_app/services/api_service.dart';
import 'node_list_page.dart';

class HubListPage extends StatefulWidget {
  const HubListPage({Key? key}) : super(key: key);
  @override
  _HubListPageState createState() => _HubListPageState();
}

class _HubListPageState extends State<HubListPage> {
  List<Hub> _hubs = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadHubs();
  }

  Future<void> _loadHubs() async {
    try {
      final hubs = await ApiService.fetchHubs();
      setState(() { _hubs = hubs; _loading = false; });
    } catch (e) {
      setState(() { _loading = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error loading hubs')));
    }
  }

  Future<void> _showHubForm({Hub? hub}) async {
    final nameCtrl = TextEditingController(text: hub?.name);
    final ipCtrl   = TextEditingController(text: hub?.ip);
    final formKey = GlobalKey<FormState>();

    final isEditing = hub != null;
    await showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: Text(isEditing ? 'Edit Hub' : 'Add Hub'),
          content: Form(
            key: formKey,
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              TextFormField(
                controller: nameCtrl,
                decoration: InputDecoration(labelText: 'Name'),
                validator: (v) => v==null||v.isEmpty?'Required':null,
              ),
              TextFormField(
                controller: ipCtrl,
                decoration: InputDecoration(labelText: 'IP or URL'),
                validator: (v) => v==null||v.isEmpty?'Required':null,
              ),
            ]),
          ),
          actions: [
            TextButton(onPressed:()=>Navigator.pop(context), child:Text('Cancel')),
            TextButton(onPressed: () async {
              if (!formKey.currentState!.validate()) return;
              final name = nameCtrl.text.trim();
              var ip = ipCtrl.text.trim();
              if (!ip.startsWith('http')) ip = 'http://$ip';
              try {
                if (isEditing) {
                  await ApiService.updateHub(hub!.id, name, ip);
                } else {
                  await ApiService.createHub(name, ip);
                }
                Navigator.pop(context);
                _loadHubs();
              } catch (_) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed')));
              }
            }, child: Text('Save'))
          ],
        )
    );
  }

  Future<void> _confirmDelete(Hub hub) async {
    if (await showDialog<bool>(
        context: context,
        builder: (_) => AlertDialog(
          title: Text('Delete Hub?'),
          content: Text('Remove \"${hub.name}\"?'),
          actions: [
            TextButton(onPressed:()=>Navigator.pop(context,false), child:Text('Cancel')),
            TextButton(onPressed:()=>Navigator.pop(context,true), child:Text('Delete'))
          ],
        )
    )==true) {
      try {
        await ApiService.deleteHub(hub.id);
        _loadHubs();
      } catch (_) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Delete failed')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return Center(child:CircularProgressIndicator());
    return Scaffold(
      body: ListView.builder(
          itemCount: _hubs.length,
          itemBuilder: (ctx,i) {
            final hub = _hubs[i];
            return ListTile(
              title: Text(hub.name),
              subtitle: Text(hub.ip),
              trailing: Row(mainAxisSize: MainAxisSize.min, children:[
                IconButton(icon:Icon(Icons.edit), onPressed:()=>_showHubForm(hub:hub)),
                IconButton(icon:Icon(Icons.delete), onPressed:()=>_confirmDelete(hub)),
              ]),
              onTap: ()=>Navigator.push(context, MaterialPageRoute(
                  builder: (_) => NodeListPage(hub: hub)
              )),
            );
          }
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.add),
        onPressed: ()=>_showHubForm(),
      ),
    );
  }
}