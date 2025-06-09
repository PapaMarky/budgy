* create set of tools for:
 * documenting UI layout from existing code (generate svg from code)
 * designing UI layout (use json file with simple box descriptions)
 * generate python code with pygame_gui layout from the json

 
 JSON starting point (pseudo JSON)
 
```json
{
   UIPanel: {
     label: "",
     x: 0,
     y: 0,
     w: 200,
     h: 100,
     show-border: true,
     ui_name: "main_box",
     children: {
     	UILable: {
     	  label: "Label",
     	  x: 0,
     	  y: 0,
     	  w: 20,
     	  h: 5,
     	  show_border: true,
     	  ui_name: "main_label"
     	}
     }
   }
}
```
 