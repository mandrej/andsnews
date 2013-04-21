var tab = "   ";
blogSettings = {
    previewAutoRefresh: true,
    onShiftEnter: {keepDefault:false, replaceWith:'<br />\n'},
    onCtrlEnter:  {keepDefault:false, openWith:'\n<p>', closeWith:'</p>\n'},
    onTab:        {keepDefault:false, openWith:tab},
    markupSet: [
        {name:'headline 4', className: 'h4', key:'4', openWith:'<h4(!( class="[![class]!]")!)>', closeWith:'</h4>', placeHolder:'Title' },
        {name:'headline 5', className: 'h5', key:'5', openWith:'<h5(!( class="[![class]!]")!)>', closeWith:'</h5>', placeHolder:'Title' },
        {name:'headline 6', className: 'h6', key:'6', openWith:'<h6(!( class="[![class]!]")!)>', closeWith:'</h6>', placeHolder:'Title' },
        {name:'paragraph', className: 'p', openWith:'<p(!( class="[![class]!]")!)>', closeWith:'</p>' },
        {name:'quote', className: 'quote', openWith:'<blockquote(!( cite="[![source (url)]!]")!)>', closeWith:'</blockquote>' },
        {separator:'---------------' },
        {name:'bold text', className: 'b', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)' },
        {name:'italics', className: 'i', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)' },
        {name:'deleted', className: 's', key:'S', openWith:'<del>', closeWith:'</del>' },
        {separator:'---------------' },
        {name:'list', className: 'ul', openWith:'<li>', closeWith:'</li>\n', multiline:true, openBlockWith:'<ul>\n', closeBlockWith:'</ul>\n' },
        {name:'ordered list', className: 'ol', openWith:'<li>', closeWith:'</li>\n', multiline:true, openBlockWith:'<ol>\n', closeBlockWith:'</ol>\n' },
        {separator:'---------------' },
        {name:'table', className: 'table', dropMenu: [
                {name: 'plain table', placeholder:"text",
                    replaceWith: function(markItUp) {
                        cols = prompt("no of columns?");
                        rows = prompt("no of rows?");
                        html = '<table(!( class="[![class]!]")!)>\n'+tab+"<tbody>\n";
                        for (r = 0; r < rows; r++) {
                            html+= tab+tab+"<tr>\n";
                            for (c = 0; c < cols; c++) {
                                html += tab+tab+tab+"<td>"+(markItUp.placeholder||"")+"</td>\n";
                            }
                            html+= tab+tab+"</tr>\n";
                        }
                        html+= tab+"</tbody>\n</table>\n";
                        return html;
                    }
                },
                {name: 'header table', placeholder:"text",
                    replaceWith: function(markItUp) {
                        cols = prompt("no of columns?");
                        rows = prompt("no of rows?");
                        html = '<table(!( class="[![class]!]")!)>\n'+tab+"<thead>\n"+tab+tab+"<tr>\n";
                        for (c = 0; c < cols; c++) {
                            html += tab+tab+tab+"<th>[!["+(c+1)+". header]!]</th>\n";
                        }
                        html+= tab+tab+"</tr>\n"+tab+"</thead>\n"+tab+"<tbody>\n";
                        for (r = 0; r < rows; r++) {
                            html+= tab+tab+"<tr>\n";
                            for (c = 0; c < cols; c++) {
                                html += tab+tab+tab+"<td>"+(markItUp.placeholder||"")+"</td>\n";
                            }
                            html+= tab+tab+"</tr>\n";
                        }
                        html+= tab+"</tbody>\n</table>\n";
                        return html;
                    }, className:"thead"
                }
            ]
        },
        {name:'add row', className: 'tr', openWith:'<tr>', closeWith:'</tr>' },
        {name:'add column', className: 'td', openWith:'<(!(td|!|th)!)>', closeWith:'</(!(td|!|th)!)>' },
        {separator:'---------------' },
        {name:'add images', className: 'images', dropMenu: [
                {name:'image link', className:'imglink', 
                    replaceWith:'<img src="[![source:!:http://]!]" alt="[![alternative text]!]" />'},
                {name:'local image', className:'img',
                    beforeInsert:function() {
                    	$('#images').show();
                    }
                }
            ]
        },
        {name:'link', className: 'a', key:'L', openWith:'<a href="[![link:!:http://]!]"(!( title="[![title]!]")!)>', closeWith:'</a>', placeHolder:'text' },
        {separator:'---------------' },
        {name:'delete html tags', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } },
        {name:'show html, Alt ~ hide', className:'preview', call:'preview' }
    ]
}