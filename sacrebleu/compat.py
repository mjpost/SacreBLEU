from typing import Sequence, Optional

from .metrics import BLEU, CHRF, TER, BLEUScore, CHRFScore, TERScore


######################################################################
# Backward compatibility functions for old style API access (< 1.4.11)
######################################################################
def corpus_bleu(sys_stream: Sequence[str],
                ref_streams: Sequence[Sequence[str]],
                smooth_method='exp',
                smooth_value=None,
                force=False,
                lowercase=False,
                tokenize=BLEU.TOKENIZER_DEFAULT,
                use_effective_order=False) -> BLEUScore:
    """Produces BLEU scores along with its sufficient statistics from a source against one or more references.

    :param sys_stream: The system stream (a sequence of segments)
    :param ref_streams: A list of one or more reference streams (each a sequence of segments)
    :param smooth_method: The smoothing method to use ('floor', 'add-k', 'exp' or 'none')
    :param smooth_value: The smoothing value for `floor` and `add-k` methods. `None` falls back to default value.
    :param force: Ignore data that looks already tokenized
    :param lowercase: Lowercase the data
    :param tokenize: The tokenizer to use
    :return: a `BLEUScore` object
    """
    metric = BLEU(
        lowercase=lowercase, force=force, tokenize=tokenize,
        smooth_method=smooth_method, smooth_value=smooth_value)

    return metric.corpus_score(sys_stream, ref_streams, use_effective_order)


def raw_corpus_bleu(sys_stream: Sequence[str],
                    ref_streams: Sequence[Sequence[str]],
                    smooth_value: Optional[float] = BLEU.SMOOTH_DEFAULTS['floor']) -> BLEUScore:
    """Convenience function that wraps corpus_bleu().
    This is convenient if you're using sacrebleu as a library, say for scoring on dev.
    It uses no tokenization and 'floor' smoothing, with the floor default to 0.1.

    :param sys_stream: the system stream (a sequence of segments)
    :param ref_streams: a list of one or more reference streams (each a sequence of segments)
    :param smooth_value: The smoothing value for `floor`. If not given, the default of 0.1 is used.
    :return: Returns a `BLEUScore` object.
    """
    return corpus_bleu(
        sys_stream, ref_streams, smooth_method='floor',
        smooth_value=smooth_value, force=True, tokenize='none',
        use_effective_order=True)


def sentence_bleu(hypothesis: str,
                  references: Sequence[str],
                  smooth_method: str = 'exp',
                  smooth_value: float = None,
                  lowercase: bool = False,
                  tokenize=BLEU.TOKENIZER_DEFAULT,
                  use_effective_order: bool = True) -> BLEUScore:
    """
    Computes BLEU on a single sentence pair.

    Disclaimer: computing BLEU on the sentence level is not its intended use,
    BLEU is a corpus-level metric.

    :param hypothesis: Hypothesis string.
    :param references: Sequence of reference strings.
    :param smooth_method: The smoothing method to use ('floor', 'add-k', 'exp' or 'none')
    :param smooth_value: The smoothing value for `floor` and `add-k` methods. `None` falls back to default value.
    :param lowercase: Lowercase the data
    :param tokenize: The tokenizer to use
    :param use_effective_order: Account for references that are shorter than the largest n-gram.
    :return: Returns a `BLEUScore` object.
    """
    metric = BLEU(
        lowercase=lowercase, tokenize=tokenize, force=False,
        smooth_method=smooth_method, smooth_value=smooth_value)

    return metric.sentence_score(hypothesis, references, use_effective_order)


def corpus_chrf(hypotheses: Sequence[str],
                references: Sequence[Sequence[str]],
                char_order: int = CHRF.CHAR_ORDER,
                word_order: int = CHRF.WORD_ORDER,
                beta: float = CHRF.BETA,
                remove_whitespace: bool = True) -> CHRFScore:
    """
    Computes ChrF++ on a corpus.

    :param hypotheses: Stream of hypotheses.
    :param references: Stream of references.
    :param char_order: Maximum character n-gram order.
    :param word_order: Maximum word n-gram order.
    :param beta: Defines importance of recall w.r.t precision. If beta=1, same importance.
    :param remove_whitespace: Whether to delete all whitespace from hypothesis and reference strings.
    :return: A `CHRFScore` object.
    """
    metric = CHRF(
        char_order=char_order,
        word_order=word_order,
        beta=beta,
        whitespace=not remove_whitespace)
    return metric.corpus_score(hypotheses, references)


def sentence_chrf(hypothesis: str,
                  references: Sequence[str],
                  char_order: int = CHRF.CHAR_ORDER,
                  word_order: int = CHRF.WORD_ORDER,
                  beta: float = CHRF.BETA,
                  remove_whitespace: bool = True) -> CHRFScore:
    """
    Computes ChrF++ on a single sentence pair.

    :param hypothesis: Hypothesis string.
    :param references: Reference string(s).
    :param char_order: Maximum character n-gram order.
    :param word_order: Maximum word n-gram order.
    :param beta: Defines importance of recall w.r.t precision. If beta=1, same importance.
    :param remove_whitespace: Whether to delete whitespaces from hypothesis and reference strings.
    :return: A `CHRFScore` object.
    """
    metric = CHRF(
        char_order=char_order,
        word_order=word_order,
        beta=beta,
        whitespace=not remove_whitespace)
    return metric.sentence_score(hypothesis, references)


def corpus_ter(hypotheses: Sequence[str],
               references: Sequence[Sequence[str]],
               normalized: bool = False,
               no_punct: bool = False,
               asian_support: bool = False,
               case_sensitive: bool = False) -> TERScore:
    """
    Computes TER on a corpus.

    :param hypotheses: Stream of hypotheses.
    :param references: Stream of references.
    :param normalized: Enable character normalization.
    :param no_punct: Remove punctuation.
    :param asian_support: Enable special treatment of Asian characters.
    :param case_sensitive: Enables case-sensitivity.
    :return: A `TERScore` object.
    """
    metric = TER(
        normalized=normalized,
        no_punct=no_punct,
        asian_support=asian_support,
        case_sensitive=case_sensitive)
    return metric.corpus_score(hypotheses, references)


def sentence_ter(hypothesis: str,
                 references: Sequence[str],
                 normalized: bool = False,
                 no_punct: bool = False,
                 asian_support: bool = False,
                 case_sensitive: bool = False) -> TERScore:
    """
    Computes TER on a single sentence pair.

    :param hypothesis: Hypothesis string.
    :param references: Reference string(s).
    :param normalized: Enable character normalization.
    :param no_punct: Remove punctuation.
    :param asian_support: Enable special treatment of Asian characters.
    :param lowercase: Lowercase all sentences.
    :return: A `TERScore` object.
    """
    metric = TER(
        normalized=normalized,
        no_punct=no_punct,
        asian_support=asian_support,
        case_sensitive=case_sensitive)
    return metric.sentence_score(hypothesis, references)
