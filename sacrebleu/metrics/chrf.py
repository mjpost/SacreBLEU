from itertools import zip_longest
from typing import List, Iterable, Union

from ..tokenizers import BaseTokenizer, TokenizerChrf

from .base import BaseScore, Signature
from .helpers import extract_char_ngrams


class CHRFSignature(Signature):
    def __init__(self, args):
        super().__init__(args)

        self._abbr.update({
            'numchars': 'n',
            'space': 's',
            'case': 'c',
        })

        self.info.update({
            'space': str(self.args['whitespace']).lower(),
            'case': 'lc' if self.args['lowercase'] else 'mixed',
            'numchars': self.args['order'],
        })


class CHRFScore(BaseScore):
    def __init__(self, score, beta, order):
        super().__init__(score)

        self.beta = beta
        self.order = order
        self.prefix = 'chrF{0:d}'.format(self.beta)

    def format(self, width=2, score_only=False, signature=''):
        # NOTE: Being 0-1 scaled, a default width of 1 is too small for chrF
        width += 1
        if score_only:
            return '{0:.{1}f}'.format(self.score, width)

        prefix = "{}+{}".format(self.prefix, signature) if signature else self.prefix
        return '{pr} = {sc:.{w}f}'.format(pr=prefix, sc=self.score, w=width)


class CHRF:
    """Computes the chrF metric given hypotheses and references.

    Args:
        whitespace: If True, includes the whitespace character in chrF computation.
        order: chrF character order
        beta: chrF Beta parameter
        lowercase: Lowercase sentences prior computation
        num_refs: Number of references (not functional for chrF as of now)
    """

    # Default values for CHRF
    ORDER = 6

    # default to 2 (per http://www.aclweb.org/anthology/W16-2341)
    BETA = 2

    def __init__(self, whitespace: bool = False,
                 order: int = ORDER,
                 beta: float = BETA,
                 lowercase: bool = False,
                 num_refs: int = 1):
        self.name = 'chrf'
        self.beta = beta
        self.order = order
        self.num_refs = num_refs
        self.lowercase = lowercase
        self.whitespace = whitespace
        self.signature = CHRFSignature(self.__dict__)

        if self.whitespace:
            self.tokenizer = BaseTokenizer()
        else:
            self.tokenizer = TokenizerChrf()

    @staticmethod
    def compute_chrf(statistics: List[int],
                     order: int,
                     beta: float) -> CHRFScore:

        score = 0.0
        avg_recall = 0.0
        avg_precision = 0.0
        effective_order = 0

        for i in range(order):
            hypotheses_ngrams = statistics[3 * i + 0]
            references_ngrams = statistics[3 * i + 1]
            common_ngrams = statistics[3 * i + 2]
            if hypotheses_ngrams > 0 and references_ngrams > 0:
                avg_precision += common_ngrams / hypotheses_ngrams
                avg_recall += common_ngrams / references_ngrams
                effective_order += 1

        if effective_order == 0:
            avg_precision, avg_recall = 0.0, 0.0
        else:
            avg_precision /= effective_order
            avg_recall /= effective_order

        if avg_precision + avg_recall == 0:
            score = 0.0
        else:
            beta_square = beta ** 2
            score = (1 + beta_square) * (avg_precision * avg_recall)
            score /= ((beta_square * avg_precision) + avg_recall)

        return CHRFScore(score, beta, order)

    def get_sentence_statistics(self, hypothesis: str,
                                references: List[str]) -> List[int]:
        # NOTE: multi-reference not supported yet
        reference = references[0]

        hypothesis = self.tokenizer(hypothesis)
        reference = self.tokenizer(reference)
        statistics = [0] * (self.order * 3)
        for i in range(self.order):
            n = i + 1
            hypothesis_ngrams = extract_char_ngrams(hypothesis, n)
            reference_ngrams = extract_char_ngrams(reference, n)
            common_ngrams = hypothesis_ngrams & reference_ngrams
            statistics[3 * i + 0] = sum(hypothesis_ngrams.values())
            statistics[3 * i + 1] = sum(reference_ngrams.values())
            statistics[3 * i + 2] = sum(common_ngrams.values())
        return statistics

    def sentence_score(self, hypothesis: str, references: List[str]) -> CHRFScore:
        """
        Computes ChrF on a single sentence pair.

        :param hypothesis: Hypothesis string.
        :param references: Reference string(s).
        :return: Chrf score.
        """
        assert not isinstance(references, str), \
            "sentence_score needs a list of references, not a single string"
        stats = self.get_sentence_statistics(hypothesis, references)
        return self.compute_chrf(stats, self.order, self.beta)

    def corpus_score(self, sys_stream: Union[str, Iterable[str]],
                     ref_streams: Union[str, List[Iterable[str]]]) -> CHRFScore:
        """
        Computes Chrf on a corpus.

        :param hypotheses: Stream of hypotheses.
        :param references: Stream of references.
        :return: Chrf score.
        """

        # Add some robustness to the input arguments
        if isinstance(sys_stream, str):
            sys_stream = [sys_stream]

        if isinstance(ref_streams, str):
            ref_streams = [[ref_streams]]

        corpus_statistics = [0] * (self.order * 3)

        fhs = [sys_stream] + ref_streams
        for lines in zip_longest(*fhs):
            if None in lines:
                raise EOFError("Source and reference streams have different lengths!")

            # Unpack
            hypothesis, *refs = lines

            statistics = self.get_sentence_statistics(hypothesis, refs)
            for i in range(len(statistics)):
                corpus_statistics[i] += statistics[i]

        return self.compute_chrf(corpus_statistics, self.order, self.beta)
