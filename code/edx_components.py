import sys
import os
from hashlib import md5

module_dir = os.path.dirname(__file__)
sys.path.extend(module_dir)

from IPython import display
import feedparser
from getyoutubecc import save_youtube_cc

__all__ = ['MoocVideo', 'PreprintReference', 'MoocDiscussion',
            'MoocCheckboxesAssessment', 'MoocMultipleChoiceAssessment',
            'MoocPeerAssessment', 'MoocSelfAssessment']

class MoocComponent(object):
    def __repr__(self):
        return '{0}(**{1})'.format(self.__class__.__name__, repr(self.param))


class MoocVideo(MoocComponent, display.YouTubeVideo):
    def __init__(self, id, src_location=None, display_name="", download_track='true',
                 download_video='true', show_captions='true', **kwargs):
        """A video component of an EdX mooc embeddable in IPython notebook."""
        tmp = locals()
        del tmp['kwargs'], tmp['self']
        del tmp['id'], tmp['src_location']
        kwargs.update(tmp)
        kwargs['youtube_id_1_0'] = id
        kwargs['youtube'] ="1.00:%s" % id

        # Add source if provided
        loc = ("http://delftxdownloads.tudelft.nl/"
               "TOPOCMx-QuantumKnots/TOPOCMx-{0}-video.720.mp4")
        if src_location is not None:
            kwargs['source'] = loc.format(src_location)

        # Try to grab subtitles from YouTube.
        try:
            save_youtube_cc(id, "../edx_skeleton/static/subs_" + id + ".srt.sjson")
            kwargs['sub'] = id
        except RuntimeError as e:
            if e.message == 'No CC available':
                pass
            else:
                raise(e)

        self.param = kwargs
        super(MoocVideo, self).__init__(id)


class PreprintReference(object):
    def __init__(self, index, description="", show_abstract=True):
        """Formatted basic information from arxiv preprint."""

        arxiv_query = "http://export.arxiv.org/api/query?id_list="
        self.index = index
        self.show_abstract = show_abstract
        self.description = description
        self.data = feedparser.parse(arxiv_query + index)

    def _repr_html_(self):
        data = self.data
        ind = self.index
        title = data['entries'][0]['title']
        s = '<h3 class="title mathjax">' + title + '</h3>'

        s += '<p><a href=http://arxiv.org/abs/%s>http://arxiv.org/abs/%s</a><br>' % (ind, ind)

        s += '<div class="authors">'
        s += ", ".join(author.name for author in data['entries'][0]['authors'])
        s += '</div></p>'

        if self.show_abstract:
            s += '<p><blockquote class="abstract mathjax">'
            s += data['entries'][0]['summary']
            s += '</blockquote></p>'

        if self.description:
            s += '<p><b>Hint:</b> %s </p>' % self.description

        return s


class MoocPeerAssessment(MoocComponent):
    def __init__(self, must_grade=5, must_be_graded_by=3, due=7, review_due=14,
                 url_name=None, **kwargs):

        self.placeholder = ('<p><b> Read one of the above papers and see how it is\n'
                            'related to the current topic.</b></p>\n'
                            '<p><b>In the live version of the course, you would '
                            'need to write a summary which is then assessed by '
                            'your peers.</b></p>')

        tmp = locals()
        del tmp['kwargs'], tmp['self']
        kwargs.update(tmp)

        with open(module_dir + '/xmls/openassessment_peer.xml', 'r') as content_file:
            openassessment_peer = content_file.read()

        kwargs['openassessment_peer'] = openassessment_peer

        self.param = kwargs

    def _repr_html_(self):
        return self.placeholder


class MoocSelfAssessment(MoocComponent):
    def __init__(self, due=7, review_due=14, url_name=None, **kwargs):

        tmp = locals()
        del tmp['kwargs'], tmp['self']
        kwargs.update(tmp)

        self.placeholder = ('<p><b> MoocSelfAssessment description</b></p>\n'
                            '<p><b>In the live version of the course, you would '
                            'need to share your solution and grade yourself.'
                            '</b></p>')

        with open(module_dir + '/xmls/openassessment_self.xml', 'r') as content_file:
            openassessment_self = content_file.read()

        kwargs['openassessment_self'] = openassessment_self

        self.param = kwargs

    def _repr_html_(self):
        return self.placeholder


class MoocCheckboxesAssessment(MoocComponent):
    def __init__(self, question, answers, correct_answers, max_attempts=2,
                 display_name="Question", **kwargs):
        """
        MoocCheckboxesAssessment component

        input types
        -----------

        question : string
        answers : list of strings
        correct_answers : list of int

        """
        tmp = locals()
        del tmp['kwargs'], tmp['self']
        kwargs.update(tmp)

        self.param = kwargs

    def _get_html_repr(self):
        param = self.param
        s = '<h4>%s</h4>' % param['question']
        s += '<form><input type="checkbox">  '
        s += '<br><input type="checkbox">  '.join(param['answers'])
        s += '</form>'

        answer = 'The correct answer{0}:<br>'.format('s are' if
                                                  len(param['correct_answers']) > 1
                                                  else ' is')
        tmp = []
        for i in param['correct_answers']:
            tmp.append(param['answers'][i])
        answer += ', '.join(t for t in tmp)
        answer += '.'
        try:
            answer += '<br><i>' + param['explanation'] + '</i>'
        except KeyError:
            pass

        s += """
        <button title="Click to show/hide content" type="button"
        onclick="if(document.getElementById('{0}')
         .style.display=='none') {{document.getElementById('{0}')
         .style.display=''}}else{{document.getElementById('{0}')
         .style.display='none'}}">Show answer</button>

        <div id="{0}" style="display:none">
        {1} <br>
        </div>    """
        return s.format(md5(repr(self)).hexdigest(), answer)

    def _repr_html_(self):
        return self._get_html_repr()


class MoocMultipleChoiceAssessment(MoocComponent):
    def __init__(self, question, answers, correct_answer, max_attempts=2,
                 display_name="Question", **kwargs):
        """
        MoocMultipleChoiceAssessment component

        Parameters:
        -----------

        question : string
        answers : list of strings
        correct_answers : int

        """
        tmp = locals()
        del tmp['kwargs'], tmp['self']
        kwargs.update(tmp)

        self.param = kwargs

    def _get_html_repr(self):
        param = self.param
        s = '<h4>%s</h4>' % param['question']
        s+= '<form>'
        for ans in param['answers']:
            s += '<input type="radio" name="answer" value="%s">' % ans + ans + '<br>'
        s+= '</form>'

        answer = 'The correct answer is: <br>'
        answer += param['answers'][param['correct_answer']]
        try:
            answer += '<br><i>' + param['explanation'] + '</i>'
        except KeyError:
            pass

        s += """
        <button title="Click to show/hide content" type="button"
        onclick="if(document.getElementById('{0}')
         .style.display=='none') {{document.getElementById('{0}')
         .style.display=''}}else{{document.getElementById('{0}')
         .style.display='none'}}">Show answer</button>

        <div id="{0}" style="display:none">{1}</div>"""
        return s.format(md5(repr(self)).hexdigest(), answer)

    def _repr_html_(self):
        return self._get_html_repr()


class MoocDiscussion(MoocComponent):
    def __init__(self, discussion_category, discussion_target, display_name=None,
                 discussion_id=None, **kwargs):

        tmp = locals()
        del tmp['kwargs'], tmp['self']
        kwargs.update(tmp)

        if display_name is None:
            kwargs['display_name'] = discussion_target

        if discussion_id is None:
            kwargs['discussion_id'] = md5(discussion_category + discussion_target).hexdigest()

        self.param = kwargs

    def _repr_html_(self):
        return "<p><b>Discussion</b> entitled '{0}' is available in the online version of the course.</p>".format(self.param['display_name'])
