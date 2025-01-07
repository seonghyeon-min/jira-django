class EulaConfig :
    def __init__(self) :
        self.terms_mapping = {
            "음성약관1": "음성 정보",
            "음성약관2": "음성 정보2",
            "LG쇼핑약관": "LG Shopping 약관",
            "맞춤형광고약관": "맞춤형 광고",
            "시청정보약관": "시청 정보",
            "최초동의": "최초 동의",
            "ACR광고약관": "ACR 광고약관",
            "기본약관": "기본 약관",
            "전체동의": "전체 동의"
        }
        
    def get_terms_mapping(self) :
        return self.terms_mapping