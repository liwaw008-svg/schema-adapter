from conftest import CONTRACT
FIELDS=['/customer/id','/invoice/total']
def setup(vm,deploy,a,b):
 vm.warp('2035-01-01T00:00:00+00:00');vm.sender=a;c=deploy(CONTRACT);c.register('bridge-4','0x'+b.hex(),'Invoice v1 to v3','https://old.example/schema','https://new.example/schema',FIELDS,600);return c
def mocks(vm,bindings=None,unmapped='[]'):
 bindings=bindings or '[{"target_index":0,"source_path":"/client/id","transform":"RENAME","lossy":false},{"target_index":1,"source_path":"/amount","transform":"COERCE","lossy":true}]';vm.mock_web(r'old\.example',{'status':200,'body':'old client and amount fields'});vm.mock_web(r'new\.example',{'status':200,'body':'required customer id and invoice total'});vm.mock_web(r'map\.example',{'status':200,'body':'field translation specification'});vm.mock_llm(r'.*SchemaAdapter field bridge audit.*','{"bindings":'+bindings+',"unmapped_indexes":'+unmapped+',"lossy_indexes":[1],"note":"Every required target has traceable source provenance."}')
def test_complete_mapping_enters_review(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);direct_vm.sender=direct_bob;mocks(direct_vm);c.submit_mapping('bridge-4','https://map.example/v3');r=c.get_adapter('bridge-4');assert r['state']=='MAPPED' and r['lossy_indexes']==[1] and len(r['digests'])==3
def test_missing_target_blocks_adapter(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);direct_vm.sender=direct_bob;mocks(direct_vm,'[{"target_index":0,"source_path":"/client/id","transform":"RENAME","lossy":false}]','[1]');direct_vm.clear_mocks();direct_vm.mock_web(r'old\.example',{'status':200,'body':'old'});direct_vm.mock_web(r'new\.example',{'status':200,'body':'new'});direct_vm.mock_web(r'map\.example',{'status':200,'body':'mapping'});direct_vm.mock_llm(r'.*SchemaAdapter field bridge audit.*','{"bindings":[{"target_index":0,"source_path":"/client/id","transform":"RENAME","lossy":false}],"unmapped_indexes":[1],"lossy_indexes":[],"note":"Invoice total is unmapped."}');c.submit_mapping('bridge-4','https://map.example/v3');assert c.get_adapter('bridge-4')['state']=='BLOCKED'
def test_author_and_third_origin_enforced(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);mocks(direct_vm)
 with direct_vm.expect_revert('author mapping'):c.submit_mapping('bridge-4','https://map.example/v3')
 direct_vm.sender=direct_bob
 with direct_vm.expect_revert('third origin'):c.submit_mapping('bridge-4','https://old.example/map')
def test_validator_rejects_dropped_target(direct_vm,direct_deploy,direct_alice,direct_bob):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);mocks(direct_vm);x=c.bridges['BRIDGE-4'];r=c._inspect(x,'https://map.example/v3');assert direct_vm.run_validator(leader_result=r) is True;f=dict(r);f['bindings']=f['bindings'][:1];assert direct_vm.run_validator(leader_result=f) is False
def test_permissionless_certification(direct_vm,direct_deploy,direct_alice,direct_bob,direct_charlie):
 c=setup(direct_vm,direct_deploy,direct_alice,direct_bob);direct_vm.sender=direct_bob;mocks(direct_vm);c.submit_mapping('bridge-4','https://map.example/v3');direct_vm.warp('2035-01-01T00:10:01+00:00');direct_vm.sender=direct_charlie;c.certify('bridge-4');assert c.get_adapter('bridge-4')['state']=='CERTIFIED'
