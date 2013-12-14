var tab = "   ";
cmntSettings = {
//    previewAutoRefresh: true,
    onShiftEnter: {keepDefault:false, replaceWith:'<br />\n'},
    onCtrlEnter:  {keepDefault:false, openWith:'\n<p>', closeWith:'</p>\n'},
    onTab:        {keepDefault:false, openWith:tab},
    markupSet: [
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
//        {name:'image link', className: 'img', key:'P', replaceWith:'<img src="[![source:!:http://]!]" alt="[![alternative text]!]" />' },
//        {name:'link', className: 'a', key:'L', openWith:'<a href="[![link:!:http://]!]"(!( title="[![title]!]")!)>', closeWith:'</a>', placeHolder:'text' },
//        {separator:'---------------' },
        {name:'delete html tags', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } }
//        {name:'show html, Alt ~ hide', className:'preview', call:'preview' }
    ]
}