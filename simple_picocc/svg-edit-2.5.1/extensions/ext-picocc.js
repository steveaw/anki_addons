//Based  on Image Occlusion 2.0  Author Contact: tmbb@campus.ul.pt
svgEditor.addExtension("Picocc", function() {
                return {
                        name: "Pic Occ",
			// For more notes on how to make an icon file, see the source of
			// the hellorworld-icon.xml
			svgicons: "extensions/picocc-icon.xml",
			
			// Multiple buttons can be added in this array
			buttons: [
            
                                /////////////////////////////////////
                                // Button for PicOccNoteGeneratorSingle
                                /////////////////////////////////////
                                {
				id: "add_notes_single_mask", 
				type: "mode", 
				title: "Create a single card", 
				events: {
					"click": function() {
						var svg_contents = svgCanvas.svgCanvasToString();
                                                pyObj.add_notes_single_mask(svg_contents);
                                                }
                                        }
                                },
                                /////////////////////////////////////
                                // Button for PicOccNoteGeneratorSeparate
                                /////////////////////////////////////
                                {
				id: "add_notes_separating_masks", 
				type: "mode", 
				title: "Create separate cards", 
				events: {
					"click": function() {
						var svg_contents = svgCanvas.svgCanvasToString();
                                                pyObj.add_notes_separating_masks(svg_contents);
                                                }
                                        }
                                },
                                
                                /////////////////////////////////////
                                // Button for PicOccNoteGeneratorHiding
                                /////////////////////////////////////
                                {
				id: "add_notes_all_masks", 
				type: "mode", 
				title: "Create separate cards (hiding)", 
				events: {
					"click": function() {
						var svg_contents = svgCanvas.svgCanvasToString();
                                                pyObj.add_notes_all_masks(svg_contents);
                                                }
                                        }
                                },
                
                                /////////////////////////////////////
                                // Button for PicOccNoteGeneratorProgressive
                                /////////////////////////////////////
                                {
				id: "add_notes_progressive_masks", 
				type: "mode", 
				title: "add_notes_progressive_masks", 
				events: {
					"click": function() {
						var svg_contents = svgCanvas.svgCanvasToString();
                                                pyObj.add_notes_progressive_masks(svg_contents);
					}
				}}
                        ],
		};
});
