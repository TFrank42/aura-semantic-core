from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from aura_semantic_core import AuraSemanticCore

BG = (0.05, 0.05, 0.10, 1)
CARD = (0.10, 0.10, 0.18, 1)
ACCENT = (0.33, 0.55, 1.00, 1)
ACCENT2 = (0.55, 0.33, 1.00, 1)
TEXT = (0.93, 0.93, 0.97, 1)
MUTED = (0.55, 0.55, 0.65, 1)
SUCCESS = (0.25, 0.85, 0.55, 1)
WARN = (1.00, 0.65, 0.20, 1)
Window.clearcolor = BG


class AuraBtn(Button):
    def __init__(self, ac=ACCENT, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_color = ac
        self.color = (1, 1, 1, 1)
        self.font_size = dp(15)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(48)


class AuraIn(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_color = (0.14, 0.14, 0.24, 1)
        self.foreground_color = TEXT
        self.cursor_color = ACCENT
        self.hint_text_color = MUTED
        self.font_size = dp(15)
        self.padding = [dp(12), dp(12)]
        self.size_hint_y = None
        self.height = dp(48)
        self.multiline = False


class ScoreRow(BoxLayout):
    def __init__(self, token, score, rank, **kw):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            padding=[dp(8), dp(4)],
            **kw
        )
        colors = [ACCENT, ACCENT2, SUCCESS, WARN, (1, 0.4, 0.4, 1)]
        c = colors[rank % len(colors)]
        self.add_widget(Label(
            text=f'#{rank + 1}',
            color=c, bold=True,
            size_hint_x=None, width=dp(36), font_size=dp(13)
        ))
        lbl = Label(text=token, color=TEXT, halign='left', valign='middle', font_size=dp(15), bold=True)
        lbl.bind(size=lbl.setter('text_size'))
        self.add_widget(lbl)
        self.add_widget(Label(
            text=f'{score:.4f}',
            color=c, size_hint_x=None, width=dp(70), font_size=dp(13), bold=True
        ))


class HomeScreen(Screen):
    def __init__(self, core, **kw):
        super().__init__(**kw)
        self.core = core
        root = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(18))
        root.add_widget(Label(text='AURA', font_size=dp(40), bold=True, color=ACCENT, size_hint_y=None, height=dp(60)))
        root.add_widget(Label(text='Semantic Core', font_size=dp(16), color=MUTED, size_hint_y=None, height=dp(28)))
        root.add_widget(Label(
            text=f'{len(core.vocab)} tokens  {core.dim}D embeddings',
            font_size=dp(13), color=MUTED, size_hint_y=None, height=dp(22)
        ))
        root.add_widget(Widget(size_hint_y=None, height=dp(12)))
        b1 = AuraBtn(text='Word Search', ac=ACCENT)
        b1.bind(on_press=lambda _: self._go('search'))
        b2 = AuraBtn(text='Sentence Similarity', ac=ACCENT2)
        b2.bind(on_press=lambda _: self._go('similarity'))
        root.add_widget(b1)
        root.add_widget(b2)
        root.add_widget(Widget())
        self.add_widget(root)

    def _go(self, name):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = name


class SearchScreen(Screen):
    def __init__(self, core, **kw):
        super().__init__(**kw)
        self.core = core
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        bk = Button(text='<', size_hint_x=None, width=dp(44),
                    background_normal='', background_color=CARD, color=ACCENT, font_size=dp(20), bold=True)
        bk.bind(on_press=self._back)
        bar.add_widget(bk)
        t = Label(text='Word Search', font_size=dp(18), bold=True, color=TEXT, halign='left')
        t.bind(size=t.setter('text_size'))
        bar.add_widget(t)
        root.add_widget(bar)
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.inp = AuraIn(hint_text='Enter a word...')
        self.inp.bind(on_text_validate=self._search)
        go = AuraBtn(text='Go', ac=ACCENT, size_hint_x=None, width=dp(64))
        go.bind(on_press=self._search)
        row.add_widget(self.inp)
        row.add_widget(go)
        root.add_widget(row)
        self.status = Label(text='', font_size=dp(13), color=MUTED, size_hint_y=None, height=dp(24))
        root.add_widget(self.status)
        sv = ScrollView()
        self.res = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None, padding=[0, dp(4)])
        self.res.bind(minimum_height=self.res.setter('height'))
        sv.add_widget(self.res)
        root.add_widget(sv)
        self.add_widget(root)

    def _back(self, *_):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def _search(self, *_):
        tok = self.inp.text.strip().lower()
        self.res.clear_widgets()
        if not tok:
            self.status.text = 'Enter a word first.'
            return
        if self.core.get_vector(tok) is None:
            self.status.text = f'"{tok}" not in vocab.'
            self.status.color = WARN
            return
        self.status.color = SUCCESS
        self.status.text = f'Top matches for "{tok}"'
        for rank, (t, s) in enumerate(self.core.most_similar(tok, topn=10)):
            self.res.add_widget(ScoreRow(t, s, rank))


class SimilarityScreen(Screen):
    def __init__(self, core, **kw):
        super().__init__(**kw)
        self.core = core
        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        bk = Button(text='<', size_hint_x=None, width=dp(44),
                    background_normal='', background_color=CARD, color=ACCENT2, font_size=dp(20), bold=True)
        bk.bind(on_press=self._back)
        bar.add_widget(bk)
        t = Label(text='Sentence Similarity', font_size=dp(18), bold=True, color=TEXT, halign='left')
        t.bind(size=t.setter('text_size'))
        bar.add_widget(t)
        root.add_widget(bar)
        root.add_widget(Label(text='Sentence A', color=ACCENT, bold=True, size_hint_y=None, height=dp(22), halign='left', font_size=dp(13)))
        self.ia = AuraIn(hint_text='e.g. he was here')
        root.add_widget(self.ia)
        root.add_widget(Label(text='Sentence B', color=ACCENT2, bold=True, size_hint_y=None, height=dp(22), halign='left', font_size=dp(13)))
        self.ib = AuraIn(hint_text='e.g. she was here')
        root.add_widget(self.ib)
        cmp = AuraBtn(text='Compare', ac=ACCENT2)
        cmp.bind(on_press=self._cmp)
        root.add_widget(cmp)
        self.slbl = Label(text='--', font_size=dp(52), bold=True, color=ACCENT2, size_hint_y=None, height=dp(90))
        self.dlbl = Label(text='Enter two sentences and tap Compare', font_size=dp(13), color=MUTED, size_hint_y=None, height=dp(24))
        root.add_widget(self.slbl)
        root.add_widget(self.dlbl)
        root.add_widget(Widget())
        self.add_widget(root)

    def _back(self, *_):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def _cmp(self, *_):
        a, b = self.ia.text.strip(), self.ib.text.strip()
        if not a or not b:
            self.dlbl.text = 'Both fields required.'
            return
        sim = self.core.sentence_similarity(a, b)
        pct = int(sim * 100)
        if pct >= 75:
            color, desc = SUCCESS, 'Very similar'
        elif pct >= 45:
            color, desc = ACCENT, 'Somewhat similar'
        elif pct >= 20:
            color, desc = WARN, 'Loosely related'
        else:
            color, desc = (1, 0.4, 0.4, 1), 'Not similar'
        self.slbl.text = f'{pct}%'
        self.slbl.color = color
        self.dlbl.text = f'{desc}  (cosine={sim:.4f})'


class AuraApp(App):
    def build(self):
        self.title = 'AURA Semantic Core'
        core = AuraSemanticCore()
        sm = ScreenManager()
        sm.add_widget(HomeScreen(core=core, name='home'))
        sm.add_widget(SearchScreen(core=core, name='search'))
        sm.add_widget(SimilarityScreen(core=core, name='similarity'))
        return sm


if __name__ == '__main__':
    AuraApp().run()
