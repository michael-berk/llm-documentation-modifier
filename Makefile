DIRECTORY_TO_REMOVE := ./checkpoint/checkpoint.json

clean:
	@echo "Cleaning up: $(DIRECTORY_TO_REMOVE)"
	@rm -rf $DIRECTORY_TO_REMOVE