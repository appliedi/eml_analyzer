from pydantic import BaseModel, Field


class SpamAssassinDetail(BaseModel):
    name: str = Field(
        description="SpamAssassin rule name (e.g. 'BAYES_50', 'HTML_MESSAGE')"
    )
    score: float = Field(description="Points contributed by this rule")
    description: str = Field(description="Human-readable description of the rule")


class SpamAssassinReport(BaseModel):
    score: float = Field(
        description="Total SpamAssassin score (typically spam if > 5.0)"
    )
    details: list[SpamAssassinDetail] = Field(
        default_factory=list, description="Individual rules that fired during analysis"
    )

    def is_spam(self, level: float = 5.0) -> bool:
        return self.score is None or self.score > level
