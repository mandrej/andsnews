var tab = "   ";
blogSettings = {
    previewAutoRefresh: true,
    onShiftEnter: {keepDefault:false, replaceWith:'<br />\n'},
    onCtrlEnter:  {keepDefault:false, openWith:'\n<p>', closeWith:'</p>\n'},
    onTab:        {keepDefault:false, openWith:tab},
    markupSet: [
        {name:'наслов 4', className: 'h4', key:'4', openWith:'<h4(!( class="[![class]!]")!)>', closeWith:'</h4>', placeHolder:'Наслов' },
        {name:'наслов 5', className: 'h5', key:'5', openWith:'<h5(!( class="[![class]!]")!)>', closeWith:'</h5>', placeHolder:'Наслов' },
        {name:'наслов 6', className: 'h6', key:'6', openWith:'<h6(!( class="[![class]!]")!)>', closeWith:'</h6>', placeHolder:'Наслов' },
        {name:'параграф', className: 'p', openWith:'<p(!( class="[![class]!]")!)>', closeWith:'</p>' },
        {name:'навођење', className: 'quote', openWith:'<blockquote(!( cite="[![извор (url)]!]")!)>', closeWith:'</blockquote>' },
        {separator:'---------------' },
        {name:'масна слова', className: 'b', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)' },
        {name:'коса слова', className: 'i', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)' },
        {name:'преправљено', className: 's', key:'S', openWith:'<del>', closeWith:'</del>' },
        {separator:'---------------' },
        {name:'листа', className: 'ul', openWith:'<li>', closeWith:'</li>\n', multiline:true, openBlockWith:'<ul>\n', closeBlockWith:'</ul>\n' },
        {name:'нумерисана листа', className: 'ol', openWith:'<li>', closeWith:'</li>\n', multiline:true, openBlockWith:'<ol>\n', closeBlockWith:'</ol>\n' },
        {separator:'---------------' },
        {name:'табела', className: 'table', dropMenu: [
                {name: 'обична табела', placeholder:"text",
                    replaceWith: function(markItUp) {
                        cols = prompt("број колона?");
                        rows = prompt("број редова?");
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
                {name: 'са заглављем', placeholder:"text",
                    replaceWith: function(markItUp) {
                        cols = prompt("број колона?");
                        rows = prompt("број редова?");
                        html = '<table(!( class="[![class]!]")!)>\n'+tab+"<thead>\n"+tab+tab+"<tr>\n";
                        for (c = 0; c < cols; c++) {
                            html += tab+tab+tab+"<th>[!["+(c+1)+". заглавље]!]</th>\n";
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
        {name:'додај ред', className: 'tr', openWith:'<tr>', closeWith:'</tr>' },
        {name:'додај колону', className: 'td', openWith:'<(!(td|!|th)!)>', closeWith:'</(!(td|!|th)!)>' },
        {separator:'---------------' },
        {name:'дадај слике', className: 'images', dropMenu: [
                {name:'линк ка слици', className:'imglink', 
                    replaceWith:'<img src="[![извор:!:http://]!]" alt="[![алтернативни текст]!]" />'},
                {name:'локална слика', className:'img',
                    beforeInsert:function() {
                        $('#images').show();
                    }
                }
            ]
        },
        {name:'линк', className: 'a', key:'L', openWith:'<a href="[![линк:!:http://]!]"(!( title="[![наслов]!]")!)>', closeWith:'</a>', placeHolder:'текст' },
        {separator:'---------------' },
        {name:'обриши html тагове', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } },
        {name:'прикажи html, Alt ~ сакри', className:'preview', call:'preview' }
    ]
}