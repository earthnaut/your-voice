# your-voice
이 레파지토리는 디지털 취약계층을 위한 폐쇄자막 AI 자동 생성 프로젝트 레파지토리입니다.  
<br>
<br>

## git으로 협업하기

### branch 만들기  
1. `git branch [branch 이름]` : [branch 이름]이라는 브랜치를 새로 만들기
2. `git checkout [branch 이름]` : [branch 이름]으로 이동하기
<br>

### git hub에 올리기
1. `git add [수정 파일 혹은 디렉토리]` : hub에 올릴 파일 혹은 디렉토리 추가하기
2. `git status` : git add에 추가된 목록 보기
3. `git commit -m '수정사항 기록'` : 어떤 부분 수정했는지 기록하기
4. `git pull origin main` : hub에 있는 최신 main 받아오기(fetch) + 내 컴퓨터에서 수정한 부분과 main을 합치기(merge)

이때 충돌이 발생하면 < 가 >, 충돌이 나지 않으면 < 나 > 따르기  
<br>

<b>< 가 ></b>  
1. `git status` : 충돌 파일 확인하기  
여러개의 충돌 파일이 뜹니다.  
Ctrl + [파일 클릭] 해서 파일 하나하나 확인 후 수정합니다.  
VScode extention 중 gitlens를 이용하면 코드를 직접 수정할 필요 없이 유지할 코드와 삭제할 코드를 선택할 수 있습니다. (아마 git 기본 기능일수도 있음...)

2. 한 파일씩 수정 완료 할 때마다 `git add [수정 파일]`

3. 전부 수정 후 다시 충돌 파일 없는지 확인 `git status`

4. 충돌 파일이 더이상 없으면 `git commit -m '충돌 해결'`
<br>

<b>< 나 ></b>
1. `git push origin [작업중인 branch 이름]` : 해당 branch에 내가 작성한 코드 올리기  
이때 주의! `git push origin main` 하지 않습니다.
<br>

### main에 병합하기
1. 팀원은 git 마스터에게 pull request 하고싶다고 알립니다.  
   (알리지 않고 pull request하면, 내 코드가 가장 최신 main과 합쳐진 것인지 알 수 없음)

2. 팀원은 가장 최신 main을 pull 해서 충돌을 수정한 후 pull request를 요청 합니다.

3. 마스터는 코드에 문제가 없는지 확인 후 pull request를 수락합니다.

주의! 여러 팀원이 동시에 pull request하지 않습니다.  
마스터는 한사람씩 봐주며 최신 상태의 main을 유지하고, main이 꼬이지 않게 유지합니다.  
(능숙한 마스터라면 꼬여도 풀 수 있겠지만 초보자라 쉽게 엄두가 안 남)
