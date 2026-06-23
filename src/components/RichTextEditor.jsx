import { useState, useRef } from 'react';
import { 
  Bold, Italic, Underline, Link, List, ListOrdered, 
  AlignLeft, AlignCenter, AlignRight, Code, Type
} from 'lucide-react';
import { motion } from 'framer-motion';

const RichTextEditor = ({ value, onChange, label, placeholder, availableTags = [] }) => {
  const editorRef = useRef(null);
  const [showTagMenu, setShowTagMenu] = useState(false);

  const execCommand = (command, value = null) => {
    document.execCommand(command, false, value);
    editorRef.current?.focus();
  };

  const insertTag = (tag) => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      const textNode = document.createTextNode(`{${tag}}`);
      range.insertNode(textNode);
      range.setStartAfter(textNode);
      range.setEndAfter(textNode);
      selection.removeAllRanges();
      selection.addRange(range);
    } else {
      document.execCommand('insertText', false, `{${tag}}`);
    }
    setShowTagMenu(false);
    handleContentChange();
  };

  const handleContentChange = () => {
    if (editorRef.current) {
      const html = editorRef.current.innerHTML;
      onChange?.(html);
    }
  };

  const toolbarButtons = [
    { icon: Bold, command: 'bold', title: 'Bold (Ctrl+B)' },
    { icon: Italic, command: 'italic', title: 'Italic (Ctrl+I)' },
    { icon: Underline, command: 'underline', title: 'Underline (Ctrl+U)' },
    { icon: AlignLeft, command: 'justifyLeft', title: 'Align Left' },
    { icon: AlignCenter, command: 'justifyCenter', title: 'Align Center' },
    { icon: AlignRight, command: 'justifyRight', title: 'Align Right' },
    { icon: List, command: 'insertUnorderedList', title: 'Bullet List' },
    { icon: ListOrdered, command: 'insertOrderedList', title: 'Numbered List' },
    { icon: Link, command: 'createLink', title: 'Insert Link', requiresValue: true },
    { icon: Code, command: 'formatBlock', value: 'pre', title: 'Code Block' },
  ];

  const fontSizes = ['8px', '10px', '12px', '14px', '16px', '18px', '20px', '22px', '24px', '28px', '32px', '36px', '42px', '48px', '56px', '64px', '72px'];
  
  const fontFamilies = [
    // Serif Fonts
    'Georgia',
    'Palatino Linotype',
    'Book Antiqua',
    'Times New Roman',
    'Times',
    'Garamond',
    'Baskerville',
    'Cambria',
    'Didot',
    'Bodoni MT',
    'Goudy Old Style',
    'Perpetua',
    'Rockwell',
    'Century',
    'Bookman Old Style',
    
    // Sans-Serif Fonts
    'Arial',
    'Helvetica',
    'Verdana',
    'Geneva',
    'Tahoma',
    'Trebuchet MS',
    'Calibri',
    'Candara',
    'Segoe UI',
    'Franklin Gothic Medium',
    'Arial Black',
    'Impact',
    'Lucida Sans Unicode',
    'Lucida Grande',
    'Century Gothic',
    'Gill Sans',
    'Avant Garde',
    'Futura',
    'Optima',
    'Corbel',
    'Myriad Pro',
    
    // Monospace Fonts
    'Courier New',
    'Courier',
    'Lucida Console',
    'Monaco',
    'Consolas',
    'Andale Mono',
    'DejaVu Sans Mono',
    'Liberation Mono',
    
    // Cursive/Decorative Fonts
    'Comic Sans MS',
    'Brush Script MT',
    'Lucida Handwriting',
    'Papyrus',
    'Copperplate',
    'Zapfino',
    'Bradley Hand',
    'Marker Felt',
    'Chalkduster',
    'Snell Roundhand',
    
    // Modern Web Fonts
    'Open Sans',
    'Roboto',
    'Lato',
    'Montserrat',
    'Raleway',
    'Poppins',
    'Source Sans Pro',
    'Ubuntu',
    'Nunito',
    'Quicksand',
    'Mukta',
    'Karla',
    'Work Sans',
    'Fira Sans',
    'Barlow',
    'Rubik',
    'Hind',
    'Oxygen',
    'PT Sans',
    'Noto Sans',
    'Inter',
    'IBM Plex Sans',
    'DM Sans',
    'Mulish',
    'Manrope',
    'Red Hat Display',
    'Archivo',
    'Public Sans',
    'Outfit',
    'Space Grotesk',
    
    // Classic Fonts
    'Palatino',
    'Hoefler Text',
    'Big Caslon',
    'Didot',
    'American Typewriter',
    'Baskerville Old Face',
    'Bell MT',
    'Californian FB',
    'Centaur',
    'Constantia',
    'Elephant',
    'Footlight MT Light',
    'French Script MT',
    'Freestyle Script',
    'Gabriola',
    'Gigi',
    'Gloucester MT Extra Condensed',
    'Goudy Stout',
    'Haettenschweiler',
    'Harrington',
    'High Tower Text',
    'Imprint MT Shadow',
    'Informal Roman',
    'Jokerman',
    'Juice ITC',
    'Kunstler Script',
    'Wide Latin',
    'Vladimir Script',
    'Tw Cen MT',
    'Sylfaen',
    'Stencil',
    'Snap ITC',
    'Script MT Bold',
    'Ravie',
    'Rage Italic',
    'Pristina',
    'Poor Richard',
    'Playbill',
    'Parchment',
    'Palace Script MT',
    'Onyx',
    'Old English Text MT',
    'OCR A Extended',
    'Niagara Solid',
    'Niagara Engraved',
    'Mistral',
    'Magneto',
    'Lucida Fax',
    'Lucida Calligraphy',
    'Kristen ITC',
    'Forte',
    'Felix Titling',
    'Engravers MT',
    'Edwardian Script ITC',
    'Curlz MT',
    'Colonna MT',
    'Chiller',
    'Castellar',
    'Calisto MT',
    'Britannic Bold',
    'Blackadder ITC',
    'Algerian',
    'Berlin Sans FB',
    'Bernard MT Condensed',
    'Bauhaus 93',
    'Baskerville Old Face',
    'Bahnschrift',
    'Arial Narrow',
    'Arial Rounded MT Bold'
  ];

  return (
    <div className="w-full">
      {label && (
        <label className="block text-base font-bold text-gray-700 mb-2">
          {label}
        </label>
      )}

      {/* Toolbar */}
      <div className="bg-gray-100 border-2 border-gray-300 border-b-0 rounded-t-xl p-3 flex flex-wrap gap-2 items-center">
        {/* Font Family */}
        <select
          onChange={(e) => execCommand('fontName', e.target.value)}
          className="px-3 py-1.5 border-2 border-gray-300 rounded-lg text-sm font-semibold text-gray-900 bg-white hover:border-gold transition-colors min-w-[180px]"
          title="Font Family"
        >
          <option value="">Select Font...</option>
          
          <optgroup label="━━━ Popular Fonts ━━━">
            <option value="Arial">Arial</option>
            <option value="Helvetica">Helvetica</option>
            <option value="Georgia">Georgia</option>
            <option value="Times New Roman">Times New Roman</option>
            <option value="Verdana">Verdana</option>
            <option value="Calibri">Calibri</option>
            <option value="Trebuchet MS">Trebuchet MS</option>
            <option value="Tahoma">Tahoma</option>
          </optgroup>
          
          <optgroup label="━━━ Modern Web Fonts ━━━">
            <option value="Open Sans">Open Sans</option>
            <option value="Roboto">Roboto</option>
            <option value="Lato">Lato</option>
            <option value="Montserrat">Montserrat</option>
            <option value="Raleway">Raleway</option>
            <option value="Poppins">Poppins</option>
            <option value="Source Sans Pro">Source Sans Pro</option>
            <option value="Ubuntu">Ubuntu</option>
            <option value="Nunito">Nunito</option>
            <option value="Quicksand">Quicksand</option>
            <option value="Mukta">Mukta</option>
            <option value="Inter">Inter</option>
            <option value="Work Sans">Work Sans</option>
            <option value="Rubik">Rubik</option>
            <option value="Manrope">Manrope</option>
          </optgroup>
          
          <optgroup label="━━━ Serif Fonts ━━━">
            <option value="Georgia">Georgia</option>
            <option value="Palatino Linotype">Palatino Linotype</option>
            <option value="Book Antiqua">Book Antiqua</option>
            <option value="Times New Roman">Times New Roman</option>
            <option value="Garamond">Garamond</option>
            <option value="Baskerville">Baskerville</option>
            <option value="Cambria">Cambria</option>
            <option value="Didot">Didot</option>
            <option value="Bodoni MT">Bodoni MT</option>
            <option value="Goudy Old Style">Goudy Old Style</option>
            <option value="Perpetua">Perpetua</option>
            <option value="Rockwell">Rockwell</option>
            <option value="Century">Century</option>
            <option value="Bookman Old Style">Bookman Old Style</option>
          </optgroup>
          
          <optgroup label="━━━ Sans-Serif Fonts ━━━">
            <option value="Arial">Arial</option>
            <option value="Helvetica">Helvetica</option>
            <option value="Verdana">Verdana</option>
            <option value="Geneva">Geneva</option>
            <option value="Tahoma">Tahoma</option>
            <option value="Trebuchet MS">Trebuchet MS</option>
            <option value="Calibri">Calibri</option>
            <option value="Candara">Candara</option>
            <option value="Segoe UI">Segoe UI</option>
            <option value="Franklin Gothic Medium">Franklin Gothic Medium</option>
            <option value="Arial Black">Arial Black</option>
            <option value="Impact">Impact</option>
            <option value="Lucida Sans Unicode">Lucida Sans Unicode</option>
            <option value="Century Gothic">Century Gothic</option>
            <option value="Gill Sans">Gill Sans</option>
            <option value="Avant Garde">Avant Garde</option>
            <option value="Futura">Futura</option>
            <option value="Optima">Optima</option>
            <option value="Corbel">Corbel</option>
          </optgroup>
          
          <optgroup label="━━━ Monospace Fonts ━━━">
            <option value="Courier New">Courier New</option>
            <option value="Courier">Courier</option>
            <option value="Lucida Console">Lucida Console</option>
            <option value="Monaco">Monaco</option>
            <option value="Consolas">Consolas</option>
            <option value="Andale Mono">Andale Mono</option>
            <option value="DejaVu Sans Mono">DejaVu Sans Mono</option>
          </optgroup>
          
          <optgroup label="━━━ Decorative Fonts ━━━">
            <option value="Comic Sans MS">Comic Sans MS</option>
            <option value="Brush Script MT">Brush Script MT</option>
            <option value="Lucida Handwriting">Lucida Handwriting</option>
            <option value="Papyrus">Papyrus</option>
            <option value="Copperplate">Copperplate</option>
            <option value="Bradley Hand">Bradley Hand</option>
            <option value="Marker Felt">Marker Felt</option>
            <option value="Chalkduster">Chalkduster</option>
          </optgroup>
          
          <optgroup label="━━━ Classic Fonts ━━━">
            <option value="Palatino">Palatino</option>
            <option value="Hoefler Text">Hoefler Text</option>
            <option value="Big Caslon">Big Caslon</option>
            <option value="American Typewriter">American Typewriter</option>
            <option value="Constantia">Constantia</option>
            <option value="Gabriola">Gabriola</option>
            <option value="High Tower Text">High Tower Text</option>
            <option value="Goudy Stout">Goudy Stout</option>
            <option value="Haettenschweiler">Haettenschweiler</option>
            <option value="Algerian">Algerian</option>
            <option value="Bauhaus 93">Bauhaus 93</option>
            <option value="Berlin Sans FB">Berlin Sans FB</option>
            <option value="Britannic Bold">Britannic Bold</option>
            <option value="Broadway">Broadway</option>
            <option value="Castellar">Castellar</option>
          </optgroup>
          
          {fontFamilies.map(font => (
            <option key={font} value={font} style={{ display: 'none' }}>{font}</option>
          ))}
        </select>

        {/* Font Size */}
        <select
          onChange={(e) => execCommand('fontSize', e.target.value)}
          className="px-3 py-1.5 border-2 border-gray-300 rounded-lg text-sm font-semibold text-gray-900 bg-white hover:border-gold transition-colors min-w-[100px]"
          title="Font Size"
        >
          <option value="">Size...</option>
          {fontSizes.map((size, idx) => (
            <option key={size} value={idx + 1}>{size}</option>
          ))}
        </select>

        <div className="w-px h-6 bg-gray-300 mx-1"></div>

        {/* Formatting Buttons */}
        {toolbarButtons.map(({ icon: Icon, command, value, title, requiresValue }) => (
          <button
            key={command}
            type="button"
            onClick={() => {
              if (requiresValue && command === 'createLink') {
                const url = prompt('Enter URL:');
                if (url) execCommand(command, url);
              } else {
                execCommand(command, value);
              }
            }}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors group"
            title={title}
          >
            <Icon className="w-5 h-5 text-gray-700 group-hover:text-gray-900" />
          </button>
        ))}

        <div className="w-px h-6 bg-gray-300 mx-1"></div>

        {/* Insert Tag Button */}
        {availableTags.length > 0 && (
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowTagMenu(!showTagMenu)}
              className="px-4 py-2 bg-gold/10 border-2 border-gold/30 rounded-lg text-sm font-black text-gold hover:bg-gold/20 transition-colors"
            >
              <Type className="w-4 h-4 inline mr-1" />
              Insert Tag
            </button>

            {/* Tag Menu */}
            {showTagMenu && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-full left-0 mt-2 bg-white border-2 border-gray-300 rounded-xl shadow-2xl p-2 z-50 w-64 max-h-64 overflow-y-auto"
              >
                <div className="p-2 border-b-2 border-gray-200 mb-2">
                  <p className="text-xs font-black text-gray-900">Available Tags</p>
                  <p className="text-xs font-semibold text-gray-600">From uploaded CSV</p>
                </div>
                {availableTags.map(tag => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => insertTag(tag)}
                    className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors text-sm font-bold text-gray-900"
                  >
                    {`{${tag}}`}
                  </button>
                ))}
              </motion.div>
            )}
          </div>
        )}
      </div>

      {/* Editor */}
      <div
        ref={editorRef}
        contentEditable
        onInput={handleContentChange}
        dangerouslySetInnerHTML={{ __html: value }}
        className="min-h-[300px] max-h-[500px] overflow-y-auto px-4 py-3 bg-gray-50 border-2 border-gray-300 rounded-b-xl text-gray-900 font-semibold focus:outline-none focus:ring-2 focus:ring-gold/50 focus:border-gold shadow-sm"
        style={{ 
          fontSize: '14px',
          lineHeight: '1.6'
        }}
      />

      <p className="text-xs font-semibold text-gray-600 mt-2">
        💡 Tip: Use the toolbar to format text. Insert tags from your CSV columns.
      </p>
    </div>
  );
};

export default RichTextEditor;
