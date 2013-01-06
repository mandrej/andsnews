var tab = "   ";
cmntSettings = {
    previewAutoRefresh: true,
    onShiftEnter: {keepDefault:false, replaceWith:'<br />\n'},
    onCtrlEnter:  {keepDefault:false, openWith:'\n<p>', closeWith:'</p>\n'},
    onTab:        {keepDefault:false, openWith:tab},
    markupSet: [
        {name:'параграф', className: 'p', openWith:'<p(!( class="[![class]!]")!)>', closeWith:'</p>' },
        {name:'навођење', className: 'quote', openWith:'<blockquote(!( cite="[![извор (url)]!]")!)>', closeWith:'</blockquote>' },
        {separator:'---------------' },
        {name:'масна слова', className: 'b', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)' },
        {name:'коса слова', className: 'i', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)' },
        {name:'преправљено', className: 's', key:'S', openWith:'<del>', closeWith:'</del>' },
        {separator:'---------------' },
        {name:'листа', className: 'ul', openWith:'<ul>\n', closeWith:'</ul>\n' },
        {name:'нумерисана листа', className: 'ol', openWith:'<ol>\n', closeWith:'</ol>\n' },
        {name:'ставка листе', className: 'li', openWith:'<li>', closeWith:'</li>' },
        {separator:'---------------' },
        {name:'слика', className: 'img', key:'P', replaceWith:'<img src="[![извор:!:http://]!]" alt="[![алтернативни текст]!]" />' },
        {name:'линк', className: 'a', key:'L', openWith:'<a href="[![линк:!:http://]!]"(!( title="[![наслов]!]")!)>', closeWith:'</a>', placeHolder:'текст' },
        {separator:'---------------' },
        {name:'обриши html тагове', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } },
        {name:'прикажи html, Alt ~ сакри', className:'preview', call:'preview' }
    ]
}